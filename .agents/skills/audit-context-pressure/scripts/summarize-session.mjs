#!/usr/bin/env node
import {createReadStream} from 'node:fs';
import {createInterface} from 'node:readline';
import path from 'node:path';

function usage() {
  console.error('Usage: node summarize-session.mjs --session <rollout.jsonl> [--top <count>]');
  process.exit(64);
}

function arg(name, fallback = undefined) {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1];
}

const sessionPath = arg('--session');
if (!sessionPath) usage();
const topCount = Number.parseInt(arg('--top', '12'), 10);
const encoder = new TextEncoder();
const byteLength = value => encoder.encode(value).byteLength;
const byKey = () => ({count: 0, bytes: 0});
const add = (map, key, bytes) => {
  const current = map[key] ??= byKey();
  current.count += 1;
  current.bytes += bytes;
};

function nestedTypes(value, found = new Set()) {
  if (Array.isArray(value)) {
    for (const item of value) nestedTypes(item, found);
  } else if (value && typeof value === 'object') {
    if (typeof value.type === 'string') found.add(value.type);
    for (const child of Object.values(value)) nestedTypes(child, found);
  }
  return [...found].sort();
}

function stringChars(value, seen = new Set()) {
  if (typeof value === 'string') return value.length;
  if (!value || typeof value !== 'object' || seen.has(value)) return 0;
  seen.add(value);
  return Array.isArray(value)
    ? value.reduce((total, item) => total + stringChars(item, seen), 0)
    : Object.values(value).reduce((total, item) => total + stringChars(item, seen), 0);
}

function blockStats(value, stats = {types: {}, inputImageBlocks: 0, inputImageSerializedBytes: 0, inputTextChars: 0}, seen = new Set()) {
  if (!value || typeof value !== 'object' || seen.has(value)) return stats;
  seen.add(value);
  if (Array.isArray(value)) {
    for (const child of value) blockStats(child, stats, seen);
    return stats;
  }
  if (typeof value.type === 'string') {
    stats.types[value.type] = (stats.types[value.type] ?? 0) + 1;
    if (value.type === 'input_image') {
      stats.inputImageBlocks += 1;
      stats.inputImageSerializedBytes += byteLength(JSON.stringify(value));
    }
    if (value.type === 'input_text') {
      stats.inputTextChars += typeof value.text === 'string' ? value.text.length : stringChars(value);
    }
  }
  for (const child of Object.values(value)) blockStats(child, stats, seen);
  return stats;
}

function ratioPercent(usage) {
  if (!usage?.inputTokens || !usage?.contextWindow) return null;
  return Number((100 * usage.inputTokens / usage.contextWindow).toFixed(1));
}

const root = {};
const nested = {};
const flags = {toolRelated: byKey(), imageRelated: byKey(), attachmentRelated: byKey(), userRole: byKey(), assistantRole: byKey(), developerOrSystemRole: byKey()};
const buckets = {under1KiB: byKey(), '1to10KiB': byKey(), '10to100KiB': byKey(), '100KiBto1MiB': byKey(), 'over1MiB': byKey()};
const compactions = [];
const largest = [];
const tokenEvents = [];
let previousTokenUsage = null;
let lineCount = 0;
let parseErrors = 0;
let totalBytes = 0;

for await (const line of createInterface({input: createReadStream(sessionPath, {encoding: 'utf8'}), crlfDelay: Infinity})) {
  lineCount += 1;
  const bytes = byteLength(line) + 1;
  totalBytes += bytes;
  let record;
  try {
    record = JSON.parse(line);
  } catch {
    parseErrors += 1;
    continue;
  }

  const rootType = record.type ?? '<missing>';
  add(root, rootType, bytes);
  const types = nestedTypes(record.payload);
  for (const type of types) add(nested, type, bytes);

  const compactLine = line.replace(/\s/g, '');
  const toolRelated = /(function_call|tool_call|tool_result|tool_output|custom_tool_call|exec_command|apply_patch)/.test(compactLine);
  const imageRelated = /(input_image|image_url|computer_screenshot|screenshot)/.test(compactLine);
  const attachmentRelated = /(attachment|referenced_image_paths|generated_images)/.test(compactLine);
  const userRole = /"role":"user"/.test(compactLine);
  const assistantRole = /"role":"assistant"/.test(compactLine);
  const developerOrSystemRole = /"role":"(?:developer|system)"/.test(compactLine);
  if (toolRelated) add(flags, 'toolRelated', bytes);
  if (imageRelated) add(flags, 'imageRelated', bytes);
  if (attachmentRelated) add(flags, 'attachmentRelated', bytes);
  if (userRole) add(flags, 'userRole', bytes);
  if (assistantRole) add(flags, 'assistantRole', bytes);
  if (developerOrSystemRole) add(flags, 'developerOrSystemRole', bytes);

  const bucket = bytes < 1024 ? 'under1KiB' : bytes < 10 * 1024 ? '1to10KiB' : bytes < 100 * 1024 ? '10to100KiB' : bytes < 1024 * 1024 ? '100KiBto1MiB' : 'over1MiB';
  add(buckets, bucket, bytes);

  if (rootType === 'compacted') {
    const history = record.payload?.replacement_history ?? [];
    const historyBlocks = blockStats(history);
    compactions.push({
      timestamp: record.timestamp,
      bytes,
      historyItems: Array.isArray(history) ? history.length : 0,
      historyStringChars: stringChars(history),
      historyBlockTypes: historyBlocks.types,
      inputImageBlocks: historyBlocks.inputImageBlocks,
      inputImageSerializedBytes: historyBlocks.inputImageSerializedBytes,
      inputTextChars: historyBlocks.inputTextChars,
      precedingTokenUsage: previousTokenUsage,
      precedingInputRatioPercent: ratioPercent(previousTokenUsage),
      windowNumber: record.payload?.window_number ?? null,
    });
  }

  if (record.payload?.type === 'token_count') {
    const usage = record.payload.info?.last_token_usage;
    const contextWindow = record.payload.info?.model_context_window;
    if (usage) {
      previousTokenUsage = {
        timestamp: record.timestamp,
        inputTokens: usage.input_tokens ?? null,
        cachedInputTokens: usage.cached_input_tokens ?? null,
        outputTokens: usage.output_tokens ?? null,
        reasoningOutputTokens: usage.reasoning_output_tokens ?? null,
        totalTokens: usage.total_tokens ?? null,
        contextWindow,
      };
      tokenEvents.push(previousTokenUsage);
    }
  }

  largest.push({timestamp: record.timestamp, rootType, bytes, nestedTypes: types, toolRelated, imageRelated, attachmentRelated});
}

const sortEntries = map => Object.entries(map).map(([name, value]) => ({name, ...value})).sort((a, b) => b.bytes - a.bytes);
largest.sort((a, b) => b.bytes - a.bytes);
const latestCompaction = compactions.at(-1) ?? null;
const totalReplacementImageSerializedBytes = compactions.reduce((total, item) => total + item.inputImageSerializedBytes, 0);
const preCompactionRatios = compactions.map(item => item.precedingInputRatioPercent).filter(value => value !== null);

console.log(JSON.stringify({
  schemaVersion: 1,
  sessionFile: path.basename(sessionPath),
  lines: lineCount,
  parsedLines: lineCount - parseErrors,
  parseErrors,
  totalBytes,
  rootRecords: sortEntries(root),
  nestedTypes: sortEntries(nested),
  flags: sortEntries(flags),
  sizeBuckets: sortEntries(buckets),
  compactions,
  compactionSummary: {
    count: compactions.length,
    totalReplacementImageSerializedBytes,
    latestReplacementHistory: latestCompaction ? {
      inputImageBlocks: latestCompaction.inputImageBlocks,
      inputImageSerializedBytes: latestCompaction.inputImageSerializedBytes,
      inputTextChars: latestCompaction.inputTextChars,
    } : null,
    preCompactionInputRatioPercent: preCompactionRatios.length ? {
      min: Math.min(...preCompactionRatios),
      max: Math.max(...preCompactionRatios),
    } : null,
  },
  tokenUsage: {
    count: tokenEvents.length,
    first: tokenEvents[0] ?? null,
    last: tokenEvents.at(-1) ?? null,
    lastInputRatioPercent: ratioPercent(tokenEvents.at(-1)),
    maxInput: tokenEvents.reduce((max, event) => !max || (event.inputTokens ?? 0) > (max.inputTokens ?? 0) ? event : max, null),
  },
  largestRecords: largest.slice(0, Number.isFinite(topCount) ? topCount : 12),
  largestNonCompactedRecords: largest.filter(record => record.rootType !== 'compacted').slice(0, Number.isFinite(topCount) ? topCount : 12),
}, null, 2));
