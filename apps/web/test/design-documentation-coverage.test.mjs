import test from 'node:test';
import assert from 'node:assert/strict';
import {access, readFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';

const root = resolve(import.meta.dirname, '..', '..', '..');
const rootReadmePath = resolve(root, 'README.md');
const coveragePath = resolve(root, 'docs', 'imp', 'design-documentation-coverage-assessment-2026-07-13.html');
const reviewSummaryPath = resolve(root, 'docs', 'imp', 'design-documentation-review-summary-2026-07-13.html');
const p0P1ScorecardPath = resolve(root, 'docs', 'imp', 'p0-p1-completion-assessment-2026-07-12.html');
const readingGuidePath = resolve(root, 'docs', 'guide', 'implementation-context-reading-guide.md');
const hubContractPath = resolve(root, 'docs', 'spec', 'hub-ui-interaction-contract-p0.md');
const tasksContractPath = resolve(root, 'docs', 'spec', 'thread-line-tasks-ui-contract-p0.md');
const sourceContractPath = resolve(root, 'docs', 'spec', 'intake-source-adapters.md');
const chatRuntimeContractPath = resolve(root, 'docs', 'spec', 'local-llm-chat-runtime-contract-p0.md');
const candidateProposalContractPath = resolve(root, 'docs', 'spec', 'ai-candidate-proposal-contract-p0.md');
const windowsVaultArchitecturePath = resolve(root, 'docs', 'arch', 'windows-vault-ai-intake-architecture-2026-07.md');
const deployGuidePath = resolve(root, 'docs', 'guide', 'linux-listening-lounge-deploy.md');
const p1StartGatePath = resolve(root, 'docs', 'spec', 'p1-start-gate-acceptance-contract-2026-07.md');
const multiProjectPaths = [
  resolve(root, 'docs', 'product', 'multi-project-workspace-flow.md'),
  resolve(root, 'docs', 'data', 'hub-project-linkage-data-design.md'),
  resolve(root, 'docs', 'spec', 'multi-project-linkage-contract.md'),
  resolve(root, 'docs', 'arch', 'hub-vikunja-multi-project-architecture.md'),
];

test('設計書カバレッジ正本は機能・設計・実装・検証を同時に追跡する', async () => {
  const html = await readFile(coveragePath, 'utf8');
  for (const required of [
    '設計書化カバレッジ',
    '最小読込セット',
    'Hub候補・判断',
    'Hub ↔ Vikunja連携',
    'Thread Line Tasks UI',
    '運用・安全再配信',
    'ローカルLLM相談',
    'Windows Vault AI batch',
    '複数Project連携',
    '要件',
    '画面・操作',
    'データ・状態',
    '連携契約',
    '運用・復旧',
    '回帰・証跡',
    '正本設計',
    '実装読込の要否',
    'localStorage',
  ]) {
    assert.match(html, new RegExp(required.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
  assert.match(html, /docs\/guide\/implementation-context-reading-guide\.md/);
  assert.match(html, /\.\.\/product\/thread-line-workspace-requirements\.md/);
  assert.match(html, /\.\.\/spec\/intake-source-adapters\.md/);
  assert.match(html, /\.\.\/spec\/local-llm-chat-runtime-contract-p0\.md/);
  assert.match(html, /\.\.\/spec\/knowledge-vault-ai-intake-contract-p0\.md/);
  assert.match(html, /\.\.\/spec\/p1-start-gate-acceptance-contract-2026-07\.md/);
  assert.match(html, /\.\.\/spec\/vikunja-integration-contract-2026-07\.md/);
  assert.match(html, /\.\.\/data\/vikunja-integration-data-design-2026-07\.md/);
  assert.match(html, /\.\.\/arch\/vikunja-pj-general-integration-architecture-2026-07\.md/);
  assert.match(html, /\.\.\/ops\/p0-operations-runbook-2026-07\.md/);
});

test('設計書カバレッジの初期評価は機能再現の根拠がそろった5点を示す', async () => {
  const html = await readFile(coveragePath, 'utf8');
  const scores = [...html.matchAll(/scores:\[([^\]]+)\]/g)].map((match) => match[1].replace(/\s/g, ''));
  assert.equal(scores.length, 11);
  assert.ok(scores.every((score) => score === '5,5,5,5,5,5,5,5'));
  assert.match(html, /機能を再現するための正本・最小実装境界・検証がそろう行を5/);
  assert.match(html, /WindowsだけがVaultを読み/);
  assert.match(html, /P1未着手のまま/);
  assert.match(html, /実データの受入未達はP0完成度星取表で別管理/);
  assert.match(html, /実機UXの未達と視覚スタイルの承認はP0完成度星取表/);
});

test('設計書カバレッジから辿る正本とskillのローカルリンクは全て存在する', async () => {
  const html = await readFile(coveragePath, 'utf8');
  const links = [...html.matchAll(/\['[^']+',\s*'([^']+)'\]/g)].map((match) => match[1]);
  assert.equal(links.length, 64);
  assert.ok(links.includes('../spec/ai-candidate-proposal-contract-p0.md'));
  assert.ok(links.includes('../../apps/web/prompts/threadline-candidate-proposal-v3.txt'));
  await Promise.all(links.map((link) => access(resolve(dirname(coveragePath), link))));
});

test('P0/P1完成度星取表は設計書化の完了を実機受入未達と混同しない', async () => {
  const scorecard = await readFile(p0P1ScorecardPath, 'utf8');
  assert.match(scorecard, /name:'設計書化カバレッジ \/ 役割別読込境界', scores:\[5,5,5,5,5,5,5,5,5,5\], pending:\[\]/);
  assert.match(scorecard, /P0実機受入の未達は別行で管理/);
  assert.match(scorecard, /const designDocumentationCoverageRevision = '2026-07-13-v1';/);
  assert.match(scorecard, /delete overrides\[designDocumentationCoverageIndex \+ ':' \+ axisIndex\]/);
  assert.doesNotMatch(scorecard, /設計書化カバレッジ: 実装・設計書・検証を機能単位で棚卸し/);
  const script = scorecard.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script);
  assert.doesNotThrow(() => new Function(script));
});

test('PJのREADMEは設計書入口と役割別読込ガイドを案内する', async () => {
  const readme = await readFile(rootReadmePath, 'utf8');
  assert.match(readme, /docs\/README\.md/);
  assert.match(readme, /docs\/imp\/design-documentation-coverage-assessment-2026-07-13\.html/);
  assert.match(readme, /docs\/guide\/implementation-context-reading-guide\.md/);
});

test('役割別読込ガイドは実装を先に広く読まない境界を定義する', async () => {
  const guide = await readFile(readingGuidePath, 'utf8');
  for (const required of [
    'P0 Hub UI',
    'Vikunja / Tasks UI',
    'Hub ↔ Vikunja連携',
    'P0入口・候補・AI相談',
    'P1開始設計',
    'Linux配信・復旧',
    '設計書化',
    '実装を読む条件',
    '最小読込セット',
    '文書中のリンクは自動読込キューではない',
    '対象見出しとその直下の節だけを読む',
    'docs/imp/design-documentation-coverage-assessment-2026-07-13.html',
  ]) {
    assert.match(guide, new RegExp(required.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
});

test('今回補完した契約は現行P0の事実と未実装P1の開始境界を分ける', async () => {
  const [source, chat, p1, summary] = await Promise.all([
    readFile(sourceContractPath, 'utf8'),
    readFile(chatRuntimeContractPath, 'utf8'),
    readFile(p1StartGatePath, 'utf8'),
    readFile(reviewSummaryPath, 'utf8'),
  ]);
  assert.match(source, /knowledge-vault AI batchだけは/);
  assert.match(source, /db_tool\.py import-vault-batch/);
  assert.match(source, /source_sync_runs/);
  assert.match(chat, /provider失敗は`502`/);
  assert.match(chat, /書き込みtoolは提供しない/);
  assert.match(p1, /P0実装済み.*誤認せず/);
  assert.match(p1, /一時PostgreSQL/);
  assert.match(summary, /設計書化レビュー結果表/);
  assert.match(summary, /機能設計の完了/);
  assert.match(summary, /視覚レビュー要/);
});

test('共通v3の実行位置とVault sequenceは閲覧themeに依存せず再現できる', async () => {
  const [contract, architecture, deployGuide] = await Promise.all([
    readFile(candidateProposalContractPath, 'utf8'),
    readFile(windowsVaultArchitecturePath, 'utf8'),
    readFile(deployGuidePath, 'utf8'),
  ]);

  assert.match(contract, /runtimeへの組込み・実行位置/);
  assert.match(contract, /candidate_proposal\.build_request\(\)/);
  assert.match(contract, /readFileSync/);
  assert.match(contract, /callCandidateProposalLlm\(\)/);
  assert.match(contract, /system = 共通v3/);
  assert.match(architecture, /"theme":"base"/);
  assert.match(architecture, /"mirrorActors":false/);
  assert.equal((architecture.match(/sequenceDiagram/g) ?? []).length, 2);
  assert.doesNotMatch(architecture, /box rgb\(/);
  assert.match(deployGuide, /Codexへ委任する範囲/);
  assert.match(deployGuide, /codex_pjserver_ed25519/);
  assert.match(deployGuide, /ユーザーはPowerShellやSSHを開かない/);
});

test('設計書化レビュー結果表は11機能のファイル量・分割・着眼点を示す', async () => {
  const summary = await readFile(reviewSummaryPath, 'utf8');
  assert.equal((summary.match(/<tr>/g) ?? []).length - 1, 11);
  for (const heading of ['文書量（ファイル量）', '分割の仕方', '記載上の着眼点（再現条件）']) {
    assert.match(summary, new RegExp(heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
});

test('赤だったP0設計不足はHub、Tasks、複数Projectの正本へ分離される', async () => {
  const [hub, tasks, ...multiProject] = await Promise.all([
    readFile(hubContractPath, 'utf8'),
    readFile(tasksContractPath, 'utf8'),
    ...multiProjectPaths.map(path => readFile(path, 'utf8')),
  ]);
  assert.match(hub, /P0 Hub UI操作契約/);
  assert.match(hub, /#dashboard/);
  assert.match(hub, /GO.*不要.*アーカイブ/s);
  assert.match(tasks, /P0 Thread Line Tasks UI契約/);
  assert.match(tasks, /前14日から向こう62日/);
  assert.match(tasks, /KANBAN VIEW/);
  for (const document of multiProject) {
    assert.match(document, /Project/);
  }
  assert.match(multiProject[1], /hub_projects/);
  assert.match(multiProject[2], /idempotency key/);
});

test('設計書運用の3 skillsはTODOなしの名前付き手順とUIメタデータを持つ', async () => {
  const skillNames = [
    'audit-design-documentation-coverage',
    'document-implementation-contracts',
    'maintain-design-documentation',
  ];
  for (const name of skillNames) {
    const folder = resolve(root, '.agents', 'skills', name);
    const [skill, metadata] = await Promise.all([
      readFile(resolve(folder, 'SKILL.md'), 'utf8'),
      readFile(resolve(folder, 'agents', 'openai.yaml'), 'utf8'),
    ]);
    assert.match(skill, new RegExp(`name: ${name}`));
    assert.doesNotMatch(skill, /TODO/);
    assert.match(skill, /docs\/guide\/docs-management-rules\.md/);
    assert.match(metadata, /display_name:/);
    assert.match(metadata, new RegExp(`\\$${name}`));
  }
});
