import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import { createHmac, timingSafeEqual } from "node:crypto";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const port = Number.parseInt(process.env.PORT || "4173", 10);
const host = process.env.HOST || "127.0.0.1";
const dbTool = join(root, "db_tool.py");
const candidateProposalPrompt = readFileSync(join(root, "prompts", "threadline-candidate-proposal-v2.txt"), "utf8");
const bundledPython = join(process.env.USERPROFILE || "", ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "python", "python.exe");
const python = process.env.PYTHON || (existsSync(bundledPython) ? bundledPython : "python");

const types = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
};

function resolvePath(url) {
  const pathname = decodeURIComponent(new URL(url, `http://localhost:${port}`).pathname);
  const relative = pathname === "/" ? "index.html" : pathname.slice(1);
  const candidate = normalize(join(root, relative));
  if (!candidate.startsWith(root)) return null;
  if (!existsSync(candidate)) return null;
  if (!statSync(candidate).isFile()) return null;
  return candidate;
}

function readBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    request.on("error", reject);
  });
}

function sendJson(response, status, payload) {
  response.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  response.end(JSON.stringify(payload));
}

function renderChatPage(sourceHtml) {
  return sourceHtml
    .replace("<title>pj-general P0</title>", "<title>AI相談 | pj-general P0</title>")
    .replace('<body data-theme="listening-lounge">', '<body class="chat-page" data-theme="listening-lounge">');
}

function runDb(command, payload = {}) {
  const result = spawnSync(python, [dbTool, command], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, PYTHONUTF8: "1", PYTHONIOENCODING: "utf-8" },
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || `db command failed: ${command}`);
  }
  return JSON.parse(result.stdout || "{}");
}

function vikunjaConfig() {
  const config = {
    baseUrl: (process.env.VIKUNJA_BASE_URL || "").replace(/\/$/, ""),
    publicUrl: (process.env.VIKUNJA_PUBLIC_URL || process.env.VIKUNJA_BASE_URL || "").replace(/\/$/, ""),
    apiBasePath: `/${(process.env.VIKUNJA_API_BASE_PATH || "/api/v1").replace(/^\/+|\/+$/g, "")}`,
    projectId: process.env.VIKUNJA_PROJECT_ID || "",
    apiToken: process.env.VIKUNJA_API_TOKEN || "",
    webhookSecret: process.env.VIKUNJA_WEBHOOK_SECRET || "",
  };
  return config;
}

function localLlmConfig() {
  const configuredBase = (process.env.LOCAL_LLM_BASE_URL || process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434").replace(/\/$/, "");
  const baseUrl = configuredBase.endsWith("/v1") ? configuredBase : `${configuredBase}/v1`;
  const provider = process.env.LOCAL_LLM_PROVIDER
    || (process.env.OLLAMA_BASE_URL ? "ollama" : process.env.LOCAL_LLM_BASE_URL ? "openai-compatible" : "ollama");
  return {
    enabled: process.env.LOCAL_LLM_ENABLED !== "false",
    baseUrl,
    provider,
    model: process.env.LOCAL_LLM_MODEL || "gemma4:latest",
    apiKey: process.env.LOCAL_LLM_API_KEY || "",
    timeoutMs: Math.max(Number.parseInt(process.env.LOCAL_LLM_TIMEOUT_MS || "60000", 10), 5000),
    tools: process.env.LOCAL_LLM_ENABLE_TOOLS !== "false",
    think: process.env.LOCAL_LLM_THINK === "true",
  };
}

async function publicLocalLlmConfig() {
  const config = localLlmConfig();
  const configuredContextLength = Number.parseInt(process.env.LOCAL_LLM_CONTEXT_LENGTH || "", 10);
  let contextLength = Number.isFinite(configuredContextLength) && configuredContextLength > 0
    ? configuredContextLength
    : null;
  if (!contextLength && config.enabled && config.provider === "ollama") {
    try {
      const ollamaRoot = config.baseUrl.replace(/\/v1$/, "");
      const modelResponse = await fetch(`${ollamaRoot}/api/show`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ model: config.model }),
        signal: AbortSignal.timeout(healthTimeoutMs()),
      });
      if (modelResponse.ok) {
        const modelInfo = (await modelResponse.json()).model_info || {};
        const contextEntry = Object.entries(modelInfo).find(([key, value]) => (
          key.endsWith(".context_length") && Number.isFinite(Number(value)) && Number(value) > 0
        ));
        if (contextEntry) contextLength = Number(contextEntry[1]);
      }
    } catch {
      contextLength = null;
    }
  }
  return {
    enabled: config.enabled,
    baseUrl: config.baseUrl,
    provider: config.provider,
    model: config.model,
    contextLength,
    tools: config.tools,
  };
}

function healthTimeoutMs() {
  return Math.min(Math.max(Number.parseInt(process.env.HEALTH_DEPENDENCY_TIMEOUT_MS || "1500", 10), 250), 10000);
}

async function checkVikunjaHealth() {
  const config = vikunjaConfig();
  const configuredValues = [config.baseUrl, config.publicUrl, config.projectId, config.apiToken];
  if (configuredValues.every((value) => !value)) return { status: "not_configured", configured: false };
  if (configuredValues.some((value) => !value)) return { status: "misconfigured", configured: false };
  const startedAt = performance.now();
  try {
    const response = await fetch(`${config.baseUrl}${config.apiBasePath}/projects/${encodeURIComponent(config.projectId)}`, {
      headers: { authorization: `Bearer ${config.apiToken}` },
      signal: AbortSignal.timeout(healthTimeoutMs()),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return { status: "ok", configured: true, latencyMs: Math.round(performance.now() - startedAt) };
  } catch {
    return { status: "unavailable", configured: true, latencyMs: Math.round(performance.now() - startedAt) };
  }
}

async function checkLocalLlmHealth() {
  const config = localLlmConfig();
  if (!config.enabled) return { status: "disabled", enabled: false, provider: config.provider, model: config.model };
  const headers = {};
  if (config.apiKey) headers.authorization = `Bearer ${config.apiKey}`;
  const startedAt = performance.now();
  try {
    const response = await fetch(`${config.baseUrl}/models`, {
      headers,
      signal: AbortSignal.timeout(healthTimeoutMs()),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return {
      status: "ok",
      enabled: true,
      provider: config.provider,
      model: config.model,
      latencyMs: Math.round(performance.now() - startedAt),
    };
  } catch {
    return {
      status: "unavailable",
      enabled: true,
      provider: config.provider,
      model: config.model,
      latencyMs: Math.round(performance.now() - startedAt),
    };
  }
}

async function getSystemHealth() {
  const database = runDb("database-health");
  const [vikunja, localLlm] = await Promise.all([checkVikunjaHealth(), checkLocalLlmHealth()]);
  const degraded = database.status !== "ok"
    || ["misconfigured", "unavailable"].includes(vikunja.status)
    || localLlm.status === "unavailable";
  return {
    status: degraded ? "degraded" : "ok",
    checkedAt: new Date().toISOString(),
    database,
    dependencies: { vikunja, localLlm },
  };
}

function chatToolDefinitions() {
  return [
    {
      type: "function",
      function: {
        name: "get_threadline_context",
        description: "Threadlineの現在のHub候補、実行状態、Vikunja概要を取得する。推測せず、相談への回答に必要なときだけ使う。",
        parameters: {
          type: "object",
          properties: {
            scope: { type: "string", enum: ["all", "tasks", "candidates"] },
          },
          additionalProperties: false,
        },
      },
    },
  ];
}

async function getThreadlineChatContext(scope = "all") {
  const [hub, vikunja] = await Promise.all([runDb("chat-context"), getVikunjaOverview()]);
  if (scope === "tasks") return { execution_state: hub.execution_state, vikunja };
  if (scope === "candidates") return { hub: hub.hub };
  return { ...hub, vikunja };
}

function buildChatSystemPrompt(context) {
  return [
    "あなたはThreadlineのローカル相談アシスタントです。日本語で、相談相手として具体的かつ簡潔に答えてください。",
    "現在のHub候補とTasks側の情報を参照できます。情報がない場合は推測せず、確認が必要だと伝えてください。",
    "必要なら読み取り専用のget_threadline_context toolを使って、Hub候補またはTasks状況の要約を確認してください。タスク登録やGOはtoolで実行できません。",
    "回答本文には候補登録用JSONを含めないでください。候補抽出は回答後に別の共通validatorが、直近のユーザー本文だけを根拠として行います。",
    "現在のThreadline context:",
    JSON.stringify(context, null, 2),
  ].join("\n");
}

function messageContent(message) {
  if (Array.isArray(message?.content)) {
    return message.content.map((part) => typeof part === "string" ? part : part?.text || "").join("");
  }
  return String(message?.content || "");
}

function parseJsonObject(content) {
  let value = String(content || "").trim();
  if (value.startsWith("```")) {
    value = value.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  }
  return JSON.parse(value);
}

async function callCandidateProposalLlm(source, sourceRef, sourceBody, allowedTags) {
  const config = localLlmConfig();
  if (!config.enabled) throw new Error("候補抽出LLMが無効です");
  const response = await fetch(`${config.baseUrl}/chat/completions`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(config.apiKey ? { authorization: `Bearer ${config.apiKey}` } : {}),
    },
    body: JSON.stringify({
      model: config.model,
      messages: [
        { role: "system", content: candidateProposalPrompt },
        {
          role: "user",
          content: [
            `SOURCE_KIND: ${source}`,
            `SOURCE_REF: ${sourceRef}`,
            `ALLOWED_TAGS: ${JSON.stringify(allowedTags)}`,
            "SOURCE_BODY:",
            String(sourceBody || "").slice(0, 12000),
          ].join("\n"),
        },
      ],
      temperature: 0,
      max_tokens: 1800,
      stream: false,
      ...(config.provider === "ollama" ? { think: config.think } : {}),
    }),
    signal: AbortSignal.timeout(config.timeoutMs),
  });
  if (!response.ok) throw new Error("候補抽出LLMに接続できません");
  const payload = await response.json();
  const content = messageContent(payload?.choices?.[0]?.message);
  if (!content) throw new Error("候補抽出LLMからJSONがありません");
  return parseJsonObject(content);
}

function acceptedSuggestions(normalized) {
  return (normalized?.proposals || [])
    .filter((proposal) => proposal?.validation?.status === "accepted")
    .map((proposal) => ({
      title: proposal.title,
      summary: proposal.summary,
      todo: proposal.todo,
      kind: proposal.kind,
      schedule: proposal.schedule,
      confidence: proposal.confidence,
      missing: proposal.missing,
    }));
}

async function importExternalSourceWithAi(source, payload) {
  const config = runDb("candidate-proposal-config");
  if (!config.sources[source]) throw new Error(`${source} source is disabled`);
  const rawItems = source === "slack" ? (payload.messages || []) : (payload.notes || []);
  const items = [];
  try {
    for (const item of rawItems) {
      const sourceBody = String(item.text || item.content || "").trim();
      if (!sourceBody) continue;
      const identity = String(item.ts || item.id || item.createdAt || item.time || "unknown");
      const baseRef = String(item.permalink || item.url || payload.channelUrl || `${source}://intake`);
      const sourceRef = item.permalink || item.url ? baseRef : `${baseRef.replace(/\/$/, "")}/${encodeURIComponent(identity)}`;
      const output = await callCandidateProposalLlm(source, sourceRef, sourceBody, config.allowedTags);
      items.push({
        sourceRef,
        sourceBody,
        occurred: String(item.occurred || item.createdAt || payload.occurred || "").slice(0, 10) || undefined,
        output,
      });
    }
  } catch {
    const run = runDb("start-source-sync", { source, cursor_before: payload.cursor });
    runDb("finish-source-sync", {
      run_id: run.run_id,
      state: "failed",
      scanned: rawItems.length,
      failed: 1,
      error: "CandidateProposalProviderError",
    });
    throw new Error("候補抽出LLMに接続できません");
  }
  return runDb("import-source-proposals", {
    source,
    sourceLabel: payload.channelName || payload.sourceLabel || (source === "slack" ? "memo-ideas" : "Misskey"),
    allowedTags: config.allowedTags,
    cursor: payload.cursor,
    cursor_after: payload.cursor_after,
    items,
  });
}

async function callLocalLlm(history, context) {
  const config = localLlmConfig();
  if (!config.enabled) throw new Error("ローカルLLM接続が無効です");
  const system = { role: "system", content: buildChatSystemPrompt(context) };
  const messages = [system, ...history.filter((message) => ["user", "assistant"].includes(message.role)).map((message) => ({
    role: message.role,
    content: message.content,
  }))];
  const headers = { "content-type": "application/json" };
  if (config.apiKey) headers.authorization = `Bearer ${config.apiKey}`;

  async function request(withTools) {
    const providerOptions = config.provider === "ollama" ? { think: config.think } : {};
    const response = await fetch(`${config.baseUrl}/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: config.model,
        messages,
        temperature: 0.2,
        max_tokens: 1200,
        stream: false,
        ...providerOptions,
        ...(withTools ? { tools: chatToolDefinitions(), tool_choice: "auto" } : {}),
      }),
      signal: AbortSignal.timeout(config.timeoutMs),
    });
    if (!response.ok) throw new Error(`provider ${response.status}`);
    return response.json();
  }

  let payload;
  try {
    payload = await request(config.tools);
  } catch (error) {
    if (!config.tools) throw new Error("ローカルLLMに接続できません");
    try {
      payload = await request(false);
    } catch {
      throw new Error("ローカルLLMに接続できません");
    }
  }

  const firstMessage = payload?.choices?.[0]?.message;
  if (!firstMessage) throw new Error("ローカルLLMから回答がありません");
  if (Array.isArray(firstMessage.tool_calls) && firstMessage.tool_calls.length > 0) {
    const toolMessages = [...messages, firstMessage];
    for (const toolCall of firstMessage.tool_calls) {
      if (toolCall?.function?.name !== "get_threadline_context") {
        toolMessages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: JSON.stringify({ error: "unknown tool" }),
        });
        continue;
      }
      let argumentsValue = {};
      try {
        argumentsValue = JSON.parse(toolCall.function.arguments || "{}");
      } catch {
        argumentsValue = {};
      }
      const scope = ["all", "tasks", "candidates"].includes(argumentsValue.scope)
        ? argumentsValue.scope
        : "all";
      const scopedContext = await getThreadlineChatContext(scope);
      toolMessages.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: JSON.stringify(scopedContext),
      });
    }
    const response = await fetch(`${config.baseUrl}/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        model: config.model,
        messages: toolMessages,
        temperature: 0.2,
        max_tokens: 1200,
        stream: false,
        ...(config.provider === "ollama" ? { think: config.think } : {}),
      }),
      signal: AbortSignal.timeout(config.timeoutMs),
    });
    if (!response.ok) throw new Error("ローカルLLMに接続できません");
    const followup = await response.json();
    const answer = messageContent(followup?.choices?.[0]?.message).trim();
    if (!answer) throw new Error("ローカルLLMから回答本文がありません");
    return answer;
  }
  const answer = messageContent(firstMessage).trim();
  if (!answer) throw new Error("ローカルLLMから回答本文がありません");
  return answer;
}

function parseChatTaskProposals(content) {
  const pattern = /THREADLINE_TASK_PROPOSALS\s*```(?:json)?\s*([\s\S]*?)```\s*END_THREADLINE_TASK_PROPOSALS/;
  const match = content.match(pattern);
  if (!match) return { content: content.trim(), suggestions: [] };
  let suggestions = [];
  try {
    const parsed = JSON.parse(match[1]);
    suggestions = (Array.isArray(parsed) ? parsed : [parsed])
      .filter((item) => item && typeof item.title === "string" && item.title.trim())
      .slice(0, 5)
      .map((item) => ({
        title: item.title.trim().slice(0, 200),
        summary: String(item.summary || item.title).slice(0, 1000),
        todo: String(item.todo || item.title).slice(0, 500),
        kind: ["todo", "idea", "consideration", "concern", "schedule_candidate"].includes(item.kind) ? item.kind : "todo",
        schedule: String(item.schedule || "候補なし").slice(0, 200),
        confidence: ["high", "medium", "low"].includes(item.confidence) ? item.confidence : "medium",
        missing: Array.isArray(item.missing) ? item.missing.map(String).slice(0, 10) : [],
      }));
  } catch {
    suggestions = [];
  }
  return { content: content.replace(match[0], "").trim(), suggestions };
}

function emptyVikunjaOverview(reason = "not-configured") {
  return {
    available: false,
    reason,
    project: null,
    tasks: [],
    summary: { total: 0, open: 0, done: 0 },
    fetchedAt: null,
  };
}

function normalizeVikunjaTask(task, config) {
  const assignees = Array.isArray(task?.assignees)
    ? task.assignees.map((assignee) => assignee.username || assignee.name || assignee.email).filter(Boolean)
    : [];
  return {
    id: task?.id,
    title: task?.title || "無題のタスク",
    done: Boolean(task?.done),
    priority: Number(task?.priority || 0),
    percentDone: Number(task?.percent_done || 0),
    dueDate: task?.due_date || null,
    updatedAt: task?.updated || task?.updated_at || null,
    assignees,
    url: task?.id ? `${config.publicUrl}/tasks/${encodeURIComponent(task.id)}` : null,
  };
}

async function fetchVikunjaJson(config, path) {
  const apiResponse = await fetch(`${config.baseUrl}${config.apiBasePath}${path}`, {
    headers: { authorization: `Bearer ${config.apiToken}` },
    signal: AbortSignal.timeout(10000),
  });
  const responseBody = await apiResponse.text();
  if (!apiResponse.ok) throw new Error(`Vikunja API ${apiResponse.status}: ${responseBody.slice(0, 200)}`);
  return JSON.parse(responseBody || "null");
}

async function getVikunjaOverview() {
  const config = vikunjaConfig();
  if (!config.baseUrl || !config.projectId || !config.apiToken || !config.publicUrl) {
    return emptyVikunjaOverview();
  }
  try {
    const [project, taskPayload] = await Promise.all([
      fetchVikunjaJson(config, `/projects/${encodeURIComponent(config.projectId)}`),
      fetchVikunjaJson(config, `/projects/${encodeURIComponent(config.projectId)}/tasks`),
    ]);
    const tasks = (Array.isArray(taskPayload) ? taskPayload : taskPayload?.tasks || taskPayload?.data || [])
      .map((task) => normalizeVikunjaTask(task, config))
      .filter((task) => task.id !== undefined && task.id !== null)
      .sort((left, right) => String(right.updatedAt || "").localeCompare(String(left.updatedAt || "")));
    const recentLimit = Math.max(Number.parseInt(process.env.VIKUNJA_OVERVIEW_TASK_LIMIT || "8", 10), 1);
    const done = tasks.filter((task) => task.done).length;
    return {
      available: true,
      reason: null,
      project: {
        id: project?.id ?? config.projectId,
        title: project?.title || `Project #${config.projectId}`,
        url: `${config.publicUrl}/projects/${encodeURIComponent(config.projectId)}`,
      },
      tasks: tasks.slice(0, recentLimit),
      summary: { total: tasks.length, open: tasks.length - done, done },
      fetchedAt: new Date().toISOString(),
    };
  } catch (error) {
    console.warn(`Vikunja overview unavailable: ${error.message}`);
    return emptyVikunjaOverview("unavailable");
  }
}

function verifyVikunjaSignature(rawBody, signature, secret) {
  if (!signature || !secret) return false;
  const expected = createHmac("sha256", secret).update(rawBody).digest("hex");
  if (signature.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(signature, "utf8"), Buffer.from(expected, "utf8"));
}

async function createVikunjaExecution(candidateId, operationId) {
  const prepared = runDb("prepare-execution", { id: candidateId, operation_id: operationId });
  if (prepared.existing) return prepared.link;
  const config = vikunjaConfig();
  if (!config.baseUrl || !config.projectId || !config.apiToken) {
    runDb("fail-execution", {
      candidate_id: candidateId,
      attempt_id: prepared.attempt_id,
      error: "Vikunja connection is not configured",
    });
    throw new Error("Vikunja connection is not configured");
  }
  const candidate = prepared.candidate;
  const description = [candidate.summary, candidate.todo, `candidate: ${candidate.id}`].filter(Boolean).join("\n\n");
  try {
    const apiResponse = await fetch(
      `${config.baseUrl}${config.apiBasePath}/projects/${encodeURIComponent(config.projectId)}/tasks`,
      {
        method: "PUT",
        headers: {
          authorization: `Bearer ${config.apiToken}`,
          "content-type": "application/json",
        },
        body: JSON.stringify({ title: candidate.todo || candidate.title, description }),
        signal: AbortSignal.timeout(10000),
      },
    );
    const responseBody = await apiResponse.text();
    if (!apiResponse.ok) throw new Error(`Vikunja API ${apiResponse.status}: ${responseBody.slice(0, 500)}`);
    const task = JSON.parse(responseBody);
    return runDb("complete-execution", {
      candidate_id: candidateId,
      attempt_id: prepared.attempt_id,
      project_id: config.projectId,
      external_url: `${config.publicUrl}/tasks/${task.id}`,
      operation_id: operationId,
      task,
    });
  } catch (error) {
    const detail = error.cause?.message ? `${error.message}: ${error.cause.message}` : error.message;
    runDb("fail-execution", {
      candidate_id: candidateId,
      attempt_id: prepared.attempt_id,
      error: detail,
    });
    throw new Error(detail);
  }
}

async function reconcileVikunjaExecutions() {
  const syncRun = runDb("start-source-sync", { source: "vikunja_reconcile" });
  const config = vikunjaConfig();
  try {
    if (!config.baseUrl || !config.apiToken) throw new Error("Vikunja connection is not configured");
    const links = runDb("list-execution-links");
    const summary = { checked: links.length, updated: 0, detached: 0, failed: 0 };
    for (const link of links) {
      try {
        const apiResponse = await fetch(
          `${config.baseUrl}${config.apiBasePath}/tasks/${encodeURIComponent(link.external_task_id)}`,
          {
            headers: { authorization: `Bearer ${config.apiToken}` },
            signal: AbortSignal.timeout(10000),
          },
        );
        if (apiResponse.status === 404) {
          runDb("record-reconcile-result", { candidate_id: link.candidate_id, result: "detached" });
          summary.detached += 1;
          continue;
        }
        const responseBody = await apiResponse.text();
        if (!apiResponse.ok) throw new Error(`Vikunja API ${apiResponse.status}: ${responseBody.slice(0, 500)}`);
        runDb("record-reconcile-result", {
          candidate_id: link.candidate_id,
          result: "updated",
          task: JSON.parse(responseBody),
        });
        summary.updated += 1;
      } catch (error) {
        const detail = error.cause?.message ? `${error.message}: ${error.cause.message}` : error.message;
        runDb("record-reconcile-result", {
          candidate_id: link.candidate_id,
          result: "failed",
          error: detail,
        });
        summary.failed += 1;
      }
    }
    runDb("finish-source-sync", {
      run_id: syncRun.run_id,
      state: summary.failed ? "partial" : "succeeded",
      scanned: summary.checked,
      created: summary.updated,
      skipped: summary.detached,
      failed: summary.failed,
    });
    return summary;
  } catch (error) {
    runDb("finish-source-sync", { run_id: syncRun.run_id, state: "failed", failed: 1, error: error.message });
    throw error;
  }
}

async function rebuildKnowledgeVaultCandidates(payload) {
  const config = vikunjaConfig();
  if (!config.baseUrl || !config.projectId || !config.apiToken) {
    throw new Error("Vikunja connection is not configured");
  }
  const listResponse = await fetch(
    `${config.baseUrl}${config.apiBasePath}/projects/${encodeURIComponent(config.projectId)}/tasks`,
    { headers: { authorization: `Bearer ${config.apiToken}` }, signal: AbortSignal.timeout(10000) },
  );
  const listBody = await listResponse.text();
  if (!listResponse.ok) throw new Error(`Vikunja API ${listResponse.status}: ${listBody.slice(0, 500)}`);
  const parsedTasks = JSON.parse(listBody || "[]");
  const tasks = Array.isArray(parsedTasks) ? parsedTasks : parsedTasks.tasks || [];
  for (const task of tasks) {
    const deleteResponse = await fetch(
      `${config.baseUrl}${config.apiBasePath}/tasks/${encodeURIComponent(task.id)}`,
      { method: "DELETE", headers: { authorization: `Bearer ${config.apiToken}` }, signal: AbortSignal.timeout(10000) },
    );
    if (!deleteResponse.ok) {
      const detail = await deleteResponse.text();
      throw new Error(`Vikunja task ${task.id} delete failed: ${deleteResponse.status} ${detail.slice(0, 500)}`);
    }
  }
  const reset = runDb("reset-operational-data");
  const imported = runDb("import-knowledge-vault", payload);
  return { deletedTasks: tasks.length, reset, import: imported };
}

async function handleApi(request, response, url) {
  try {
    if (request.method === "GET" && url.pathname === "/api/health") {
      sendJson(response, 200, await getSystemHealth());
      return true;
    }
    if (request.method === "GET" && url.pathname === "/api/observability") {
      sendJson(response, 200, runDb("observability"));
      return true;
    }
    if (request.method === "GET" && url.pathname === "/api/bootstrap") {
      sendJson(response, 200, runDb("bootstrap"));
      return true;
    }
    if (request.method === "GET" && url.pathname === "/api/integrations/vikunja/overview") {
      sendJson(response, 200, await getVikunjaOverview());
      return true;
    }
    if (request.method === "GET" && url.pathname === "/api/chat/bootstrap") {
      const [chat, context] = await Promise.all([
        Promise.resolve(runDb("chat-bootstrap", { thread_id: "chat-default" })),
        getThreadlineChatContext(),
      ]);
      sendJson(response, 200, { ...chat, config: await publicLocalLlmConfig(), context });
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/chat/messages") {
      const body = JSON.parse((await readBody(request)) || "{}");
      const content = String(body.content || "").trim();
      if (!content) {
        sendJson(response, 400, { error: "相談内容を入力してください" });
        return true;
      }
      const threadId = body.threadId || "chat-default";
      const userMessage = runDb("chat-save-message", { thread_id: threadId, role: "user", content });
      try {
        const [history, context] = await Promise.all([
          Promise.resolve(runDb("chat-bootstrap", { thread_id: threadId })),
          getThreadlineChatContext(),
        ]);
        const rawAnswer = await callLocalLlm(history.messages, context);
        const parsed = parseChatTaskProposals(rawAnswer);
        let proposed = [];
        try {
          const proposalConfig = runDb("candidate-proposal-config");
          const sourceRef = `chat://thread/${encodeURIComponent(threadId)}/message/${userMessage.id}`;
          const output = await callCandidateProposalLlm("chat", sourceRef, content, proposalConfig.allowedTags);
          const normalized = runDb("normalize-source-proposals", {
            source: "chat",
            sourceRef,
            sourceBody: content,
            allowedTags: proposalConfig.allowedTags,
            output,
          });
          proposed = acceptedSuggestions(normalized);
        } catch {
          proposed = [];
        }
        const assistantMessage = runDb("chat-save-message", {
          thread_id: threadId,
          role: "assistant",
          content: parsed.content || "回答を生成できませんでした。",
          metadata: { model: localLlmConfig().model, suggestionCount: proposed.length },
        });
        const suggestions = proposed.length
          ? runDb("chat-create-suggestions", { thread_id: threadId, message_id: assistantMessage.id, suggestions: proposed })
          : [];
        sendJson(response, 200, { userMessage, assistantMessage, suggestions, context, config: publicLocalLlmConfig() });
      } catch (error) {
        error.statusCode = 502;
        sendJson(response, 502, { error: error.message, userMessage });
      }
      return true;
    }
    const chatSuggestionMatch = url.pathname.match(/^\/api\/chat\/suggestions\/([^/]+)\/accept$/);
    if (request.method === "POST" && chatSuggestionMatch) {
      const suggestionId = decodeURIComponent(chatSuggestionMatch[1]);
      const result = runDb("chat-accept-suggestion", { id: suggestionId });
      sendJson(response, 201, result);
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/candidates") {
      const body = await readBody(request);
      sendJson(response, 201, runDb("create-candidate", JSON.parse(body || "{}")));
      return true;
    }
    const executionMatch = url.pathname.match(/^\/api\/candidates\/([^/]+)\/execution$/);
    if (request.method === "POST" && executionMatch) {
      const candidateId = decodeURIComponent(executionMatch[1]);
      const payload = JSON.parse((await readBody(request)) || "{}");
      const link = await createVikunjaExecution(candidateId, payload.operation_id);
      sendJson(response, link.sync_state === "synced" ? 200 : 201, link);
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/integrations/vikunja/webhook") {
      const rawBody = await readBody(request);
      const config = vikunjaConfig();
      const signature = request.headers["x-vikunja-signature"] || "";
      if (!verifyVikunjaSignature(rawBody, signature, config.webhookSecret)) {
        sendJson(response, 401, { error: "invalid Vikunja signature" });
        return true;
      }
      const event = JSON.parse(rawBody || "{}");
      sendJson(
        response,
        200,
        runDb("process-vikunja-webhook", {
          raw_body: rawBody,
          external_event_id: event.event_id || null,
        }),
      );
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/integrations/vikunja/reconcile") {
      sendJson(response, 200, await reconcileVikunjaExecutions());
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/import/knowledge-vault") {
      const body = await readBody(request);
      sendJson(response, 200, runDb("import-knowledge-vault", JSON.parse(body || "{}")));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/admin/rebuild-knowledge-vault-candidates") {
      const body = await readBody(request);
      sendJson(response, 200, await rebuildKnowledgeVaultCandidates(JSON.parse(body || "{}")));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/import/slack") {
      const body = await readBody(request);
      const payload = JSON.parse(body || "{}");
      const result = payload.mode === "legacy_direct"
        ? runDb("import-slack", payload)
        : await importExternalSourceWithAi("slack", payload);
      sendJson(response, 200, result);
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/import/misskey") {
      const body = await readBody(request);
      sendJson(response, 200, await importExternalSourceWithAi("misskey", JSON.parse(body || "{}")));
      return true;
    }
    const sourceMatch = url.pathname.match(/^\/api\/admin\/sources\/([^/]+)$/);
    if (request.method === "PATCH" && sourceMatch) {
      const body = await readBody(request);
      const payload = { ...JSON.parse(body || "{}"), id: decodeURIComponent(sourceMatch[1]) };
      sendJson(response, 200, runDb("update-source", payload));
      return true;
    }
    const promptMatch = url.pathname.match(/^\/api\/admin\/prompt-templates\/([^/]+)$/);
    if (request.method === "PATCH" && promptMatch) {
      const body = await readBody(request);
      const payload = { ...JSON.parse(body || "{}"), id: decodeURIComponent(promptMatch[1]) };
      sendJson(response, 200, runDb("update-prompt-template", payload));
      return true;
    }
    const controlMatch = url.pathname.match(/^\/api\/admin\/settings\/(roles|automation|scopes)\/([^/]+)$/);
    if (request.method === "PATCH" && controlMatch) {
      const body = await readBody(request);
      const payload = {
        ...JSON.parse(body || "{}"),
        group: controlMatch[1],
        id: decodeURIComponent(controlMatch[2]),
      };
      sendJson(response, 200, runDb("update-admin-control", payload));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/admin/tags") {
      const body = await readBody(request);
      sendJson(response, 201, runDb("create-tag", JSON.parse(body || "{}")));
      return true;
    }
    const tagMatch = url.pathname.match(/^\/api\/admin\/tags\/(\d+)$/);
    if (request.method === "PATCH" && tagMatch) {
      const body = await readBody(request);
      const payload = { ...JSON.parse(body || "{}"), id: Number.parseInt(tagMatch[1], 10) };
      sendJson(response, 200, runDb("update-tag", payload));
      return true;
    }
    const statusMatch = url.pathname.match(/^\/api\/candidates\/([^/]+)\/status$/);
    if (request.method === "PATCH" && statusMatch) {
      const body = await readBody(request);
      const payload = { ...JSON.parse(body || "{}"), id: decodeURIComponent(statusMatch[1]) };
      sendJson(response, 200, runDb("update-status", payload));
      return true;
    }
    const candidateMatch = url.pathname.match(/^\/api\/candidates\/([^/]+)$/);
    if (request.method === "PATCH" && candidateMatch) {
      const body = await readBody(request);
      const payload = { ...JSON.parse(body || "{}"), id: decodeURIComponent(candidateMatch[1]) };
      sendJson(response, 200, runDb("update-candidate", payload));
      return true;
    }
    return false;
  } catch (error) {
    sendJson(response, error.statusCode || 500, { error: error.message });
    return true;
  }
}

runDb("bootstrap");

createServer(async (request, response) => {
  const url = new URL(request.url || "/", `http://localhost:${port}`);
  if (url.pathname.startsWith("/api/") && (await handleApi(request, response, url))) {
    return;
  }

  if (request.method === "GET" && url.pathname === "/chat") {
    const html = renderChatPage(readFileSync(join(root, "index.html"), "utf8"));
    response.writeHead(200, {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
    });
    response.end(html);
    return;
  }
  if (request.method === "GET" && url.pathname === "/theme-room-03") {
    response.writeHead(302, { location: "/", "cache-control": "no-store" });
    response.end();
    return;
  }

  const file = resolvePath(request.url || "/");
  if (!file) {
    response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }

  response.writeHead(200, {
    "content-type": types[extname(file)] || "application/octet-stream",
    "cache-control": "no-store",
  });
  createReadStream(file).pipe(response);
}).listen(port, host, () => {
  console.log(`pj-general web: http://${host}:${port}`);
});
