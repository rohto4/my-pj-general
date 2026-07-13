import assert from "node:assert/strict";
import { access, mkdtemp, readFile, rm } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { spawn, spawnSync } from "node:child_process";
import { createHmac } from "node:crypto";
import { createServer } from "node:http";

const require = createRequire(import.meta.url);
const webRoot = join(import.meta.dirname, "..");
const port = 4187;
const baseUrl = `http://127.0.0.1:${port}`;
const bundledPython = join(process.env.USERPROFILE || "", ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "python", "python.exe");
const python = process.env.PYTHON || bundledPython;

test("AI相談は短い画面でも会話と入力を主役にする", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const styles = await readFile(join(webRoot, "styles.css"), "utf8");
  const themeStyles = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.doesNotMatch(html, /class="section-heading chat-heading"/);
  assert.doesNotMatch(html, /class="chat-flow"/);
  assert.match(html, /<h2 id="chat-title" class="sr-only">AI相談<\/h2>/);
  assert.doesNotMatch(html, /class="chat-composer-label"/);
  assert.doesNotMatch(html, /まずは、そのまま書いてください/);
  assert.match(html, /id="chatProviderStatus"[\s\S]*id="chatModelMeta"/);
  assert.match(html, /id="chatContextMeta"/);
  assert.match(html, /class="[^"]*chat-context-strip[^"]*"/);
  assert.match(html, /class="chat-toolbar__meta"[\s\S]*id="chatProviderStatus"/);
  assert.match(html, /class="chat-composer-row"[\s\S]*id="chatPageInput"[\s\S]*type="submit">相談する/);
  assert.match(html, /class="nav-side-chat"[^>]*data-open-chat/);
  assert.match(html, /AI相談をサイドで開く/);
  assert.match(styles, /body\.chat-page \.main\s*\{[^}]*height:\s*100vh[^}]*overflow:\s*hidden/s);
  assert.match(styles, /body\.chat-page \.main > #chat\s*\{[^}]*grid-template-rows:\s*minmax\(0, 1fr\)/s);
  assert.match(styles, /body\.chat-page \.chat-panel\s*\{[^}]*block-size:\s*100%/s);
  assert.match(styles, /body\.chat-page \.chat-context-strip\s*\{[^}]*padding:\s*3px 8px/s);
  assert.match(styles, /body\.chat-page \.chat-context-stat\s*\{[^}]*justify-content:\s*flex-start/s);
  assert.match(styles, /\.chat-composer-row\s*\{[^}]*grid-template-columns:\s*minmax\(0, 1fr\) auto/s);
  assert.match(styles, /@media \(max-height: 900px\)[\s\S]*body\.chat-page \.chat-message\s*\{[^}]*font-size:/s);
  assert.match(styles, /@media \(max-height: 650px\)[\s\S]*body\.chat-page \.chat-composer textarea\s*\{[^}]*font-size:/s);
  assert.match(styles, /body\.chat-page \.topbar\s*\{[^}]*display:\s*none/s);
  assert.match(styles, /\.chat-message--user\s*\{[^}]*min-inline-size:/s);
  assert.match(themeStyles, /body\[data-theme="listening-lounge"\] \.status-pill\s*\{[^}]*color:\s*#f0e8db/s);
  assert.match(themeStyles, /body\[data-theme="listening-lounge"\] \.chat-panel\s*\{[^}]*padding:\s*0/s);
  assert.match(themeStyles, /body\.chat-page\[data-theme="listening-lounge"\] \.chat-context-strip\s*\{[^}]*padding:\s*3px 8px/s);
});

test("管理画面はsource同期・reconcile・backupの観測結果を表示する", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  assert.match(html, /id="observabilityRuns"/);
  assert.match(html, /id="observabilityMetrics"/);
  assert.match(html, /id="refreshObservability"/);
  assert.match(app, /apiJson\("\/api\/observability"\)/);
  assert.match(app, /latestBySource/);
  assert.match(app, /operations/);
});

async function waitForServer() {
  for (let index = 0; index < 30; index += 1) {
    try {
      const response = await fetch(`${baseUrl}/api/bootstrap`);
      if (response.ok) return;
    } catch {
      // 起動待ち
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("test server did not start");
}

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: { "content-type": "application/json" },
    ...options,
  });
  const body = await response.text();
  assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
  return JSON.parse(body);
}

test("P0 管理データはSQLiteに保存され、初期データにモック候補を含めない", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-p0-"));
  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(port),
      P0_DB_PATH: join(dir, "p0.sqlite"),
      LOCAL_LLM_ENABLED: "false",
      VIKUNJA_BASE_URL: "",
      VIKUNJA_PUBLIC_URL: "",
      VIKUNJA_PROJECT_ID: "",
      VIKUNJA_API_TOKEN: "",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await rm(dir, { recursive: true, force: true });
  });

  await waitForServer();
  const health = await request("/api/health");
  assert.equal(health.status, "ok");
  assert.equal(health.database.status, "ok");
  assert.equal(health.database.integrity, "ok");
  assert.equal(health.dependencies.vikunja.status, "not_configured");
  assert.equal(health.dependencies.localLlm.status, "disabled");
  assert.equal(JSON.stringify(health).toLowerCase().includes("token"), false);
  assert.equal(JSON.stringify(health).includes(dir), false);
  const promotedTheme = await fetch(`${baseUrl}/theme-room-03`, { redirect: "manual" });
  assert.equal(promotedTheme.status, 302);
  assert.equal(promotedTheme.headers.get("location"), "/");
  for (const pageId of ["theme-room-01", "theme-room-02", "theme-room-04"]) {
    const retiredPreview = await fetch(`${baseUrl}/${pageId}`);
    assert.equal(retiredPreview.status, 404);
  }
  const chatPage = await fetch(`${baseUrl}/chat`);
  const chatHtml = await chatPage.text();
  assert.equal(chatPage.status, 200);
  assert.match(chatHtml, /<body class="chat-page" data-theme="listening-lounge">/);
  assert.match(chatHtml, /id="chat"/);
  assert.match(chatHtml, /AI相談/);
  const rootPage = await fetch(baseUrl);
  const rootHtml = await rootPage.text();
  assert.doesNotMatch(rootHtml, /<body class="chat-page">/);
  assert.match(rootHtml, /<body data-theme="listening-lounge">/);
  const initial = await request("/api/bootstrap");
  assert.equal(initial.candidates.some((candidate) => /mock/i.test(JSON.stringify(candidate))), false);
  assert.ok(Array.isArray(initial.adminControls.roles));
  assert.ok(Array.isArray(initial.adminControls.automation));
  assert.ok(Array.isArray(initial.adminControls.scopes));

  const decisionCandidate = await request("/api/candidates", {
    method: "POST",
    body: JSON.stringify({ title: "判断ログ順序テスト", body: "P0受入用", kind: "todo" }),
  });
  const edited = await request(`/api/candidates/${encodeURIComponent(decisionCandidate.id)}`, {
    method: "PATCH",
    body: JSON.stringify({ title: "判断ログ順序テスト", status: "edited", operation_id: "p0-u03-edit" }),
  });
  const rejected = await request(`/api/candidates/${encodeURIComponent(decisionCandidate.id)}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: "rejected", operation_id: "p0-u03-reject" }),
  });
  const archived = await request(`/api/candidates/${encodeURIComponent(decisionCandidate.id)}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: "archived", operation_id: "p0-u03-archive" }),
  });
  assert.equal(edited.decision.operationId, "p0-u03-edit");
  assert.equal(rejected.decision.operationId, "p0-u03-reject");
  assert.equal(archived.decision.operationId, "p0-u03-archive");
  const decisionLog = (await request("/api/bootstrap")).log.filter((item) => item.title === decisionCandidate.todo);
  assert.deepEqual(decisionLog.map((item) => item.action), ["archived", "rejected", "edited", "created"]);
  assert.deepEqual(decisionLog.slice(0, 3).map((item) => item.operationId), ["p0-u03-archive", "p0-u03-reject", "p0-u03-edit"]);

  await request("/api/admin/settings/roles/owner", {
    method: "PATCH",
    body: JSON.stringify({ enabled: false }),
  });
  const createdTag = await request("/api/admin/tags", {
    method: "POST",
    body: JSON.stringify({ name: "p0-test-tag" }),
  });
  await request(`/api/admin/tags/${createdTag.id}`, {
    method: "PATCH",
    body: JSON.stringify({ visible: false }),
  });

  const persisted = await request("/api/bootstrap");
  assert.equal(persisted.adminControls.roles.find((item) => item.id === "owner").enabled, false);
  assert.equal(persisted.tags.find((tag) => tag.id === createdTag.id).visible, 0);
});

test("Ganttは固定サンプルを使わず、日付を持つSQLite候補だけを表示する", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-gantt-api-"));
  const appPort = 4193;
  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: { ...process.env, PORT: String(appPort), P0_DB_PATH: join(dir, "p0.sqlite") },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await rm(dir, { recursive: true, force: true });
  });

  const localRequest = async (path, options = {}) => {
    const response = await fetch(`http://127.0.0.1:${appPort}${path}`, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.text();
    assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
    return JSON.parse(body);
  };
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  const initial = await localRequest("/api/bootstrap");
  assert.deepEqual(initial.ganttTasks, []);

  await localRequest("/api/candidates", {
    method: "POST",
    body: JSON.stringify({
      title: "実データの予定候補",
      kind: "schedule_candidate",
      body: "SQLite候補からGanttへ表示する",
      schedule: "2026-07-15 / 45 min",
    }),
  });
  const persisted = await localRequest("/api/bootstrap");
  assert.equal(persisted.ganttTasks.length, 1);
  assert.equal(persisted.ganttTasks[0].title, "実データの予定候補 を整理する");
  assert.equal(persisted.ganttTasks[0].id.startsWith("GT-"), false);
  assert.equal(persisted.ganttTasks[0].startDate, "2026-07-15");
});

test("Vikunja結合用schemaは判断・同期・外部task状態を分離する", async () => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-vikunja-schema-"));
  try {
    const result = spawnSync(python, [join(webRoot, "db_tool.py"), "schema-info"], {
      input: "{}",
      encoding: "utf8",
      env: { ...process.env, P0_DB_PATH: join(dir, "p0.sqlite"), PYTHONUTF8: "1", PYTHONIOENCODING: "utf-8" },
    });
    assert.equal(result.status, 0, result.stderr || result.stdout);
    const schema = JSON.parse(result.stdout);
    assert.deepEqual(
      ["execution_links", "execution_task_state", "source_sync_runs", "sync_attempts", "sync_events"].filter((name) => !schema.tables.includes(name)),
      [],
    );
    assert.deepEqual(
      ["chat_threads", "chat_messages", "chat_task_suggestions"].filter((name) => !schema.tables.includes(name)),
      [],
    );
    assert.ok(schema.uniqueIndexes.sync_events.includes("dedupe_key"));
    assert.ok(schema.uniqueIndexes.sync_attempts.includes("idempotency_key"));
    assert.ok(schema.uniqueIndexes.source_sync_runs.includes("run_id"));
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});

test("source同期・reconcile・backupの結果を同じ観測APIで確認できる", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-observability-"));
  const appPort = 4195;
  const database = join(dir, "p0.sqlite");
  const backupDir = join(dir, "backups");
  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(appPort),
      P0_DB_PATH: database,
      P0_BACKUP_DIR: backupDir,
      LOCAL_LLM_ENABLED: "false",
      VIKUNJA_BASE_URL: "",
      VIKUNJA_PROJECT_ID: "",
      VIKUNJA_API_TOKEN: "",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await rm(dir, { recursive: true, force: true });
  });
  const localRequest = async (path, options = {}) => {
    const response = await fetch(`http://127.0.0.1:${appPort}${path}`, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.text();
    assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
    return JSON.parse(body);
  };
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  const before = await localRequest("/api/observability");
  assert.deepEqual(before.sourceSyncRuns, []);
  assert.deepEqual(before.latestBackups, []);

  const imported = await localRequest("/api/import/slack", {
    method: "POST",
    body: JSON.stringify({
      channelName: "memo-ideas",
      messages: [{ ts: "2026-07-12T01:02:03Z", text: "観測APIの同期結果を確認する" }],
    }),
  });
  assert.equal(imported.imported, 1);
  assert.equal(imported.syncRun.source, "slack");
  assert.equal(imported.syncRun.state, "succeeded");
  assert.equal(imported.syncRun.scanned, 1);
  assert.equal(imported.syncRun.created, 1);

  const second = await localRequest("/api/import/slack", {
    method: "POST",
    body: JSON.stringify({
      channelName: "memo-ideas",
      messages: [{ ts: "2026-07-12T01:02:03Z", text: "観測APIの同期結果を確認する" }],
    }),
  });
  assert.equal(second.imported, 0);
  assert.equal(second.syncRun.skipped, 1);

  const backup = spawnSync(python, [join(webRoot, "db_tool.py"), "backup-database"], {
    input: "{}",
    encoding: "utf8",
    env: { ...process.env, P0_DB_PATH: database, P0_BACKUP_DIR: backupDir, PYTHONUTF8: "1", PYTHONIOENCODING: "utf-8" },
  });
  assert.equal(backup.status, 0, backup.stderr || backup.stdout);

  const after = await localRequest("/api/observability");
  assert.equal(after.sourceSyncRuns.length, 2);
  assert.equal(after.sourceSyncRuns[0].source, "slack");
  assert.equal(after.sourceSyncRuns[0].state, "succeeded");
  assert.equal(after.latestBySource.slack.state, "succeeded");
  assert.equal(after.latestBackups[0].integrity, "ok");
  assert.equal(after.latestBackups[0].sha256.length, 64);
  assert.equal(after.operations.sourceCounts.slack, 1);
  assert.equal(after.operations.candidateCounts.total, 1);
  assert.equal(after.operations.candidateCounts.pending, 1);
  assert.equal(after.operations.executionCounts.linked, 0);
  assert.equal(JSON.stringify(after).includes(database), false);
});

test("SQLite backupはonline backupで世代を分け、整合性・件数・hashを返す", async () => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-backup-"));
  const database = join(dir, "p0.sqlite");
  const backupDir = join(dir, "backups");
  const env = {
    ...process.env,
    P0_DB_PATH: database,
    P0_BACKUP_DIR: backupDir,
    PYTHONUTF8: "1",
    PYTHONIOENCODING: "utf-8",
  };
  const run = (command, payload = {}) => {
    const result = spawnSync(python, [join(webRoot, "db_tool.py"), command], {
      input: JSON.stringify(payload),
      encoding: "utf8",
      env,
    });
    assert.equal(result.status, 0, result.stderr || result.stdout);
    return JSON.parse(result.stdout);
  };
  try {
    run("bootstrap");
    run("create-candidate", { title: "backup対象", body: "世代backupを確認する" });
    const first = run("backup-database");
    const second = run("backup-database");

    assert.notEqual(first.path, second.path);
    assert.equal(first.integrity, "ok");
    assert.equal(first.counts.candidates, 1);
    assert.equal(first.sha256.length, 64);
    assert.equal(first.sourceDatabaseExposed, undefined);
    await access(first.path);
    await access(second.path);

    const backupHealth = spawnSync(python, [join(webRoot, "db_tool.py"), "database-health"], {
      input: "{}",
      encoding: "utf8",
      env: { ...env, P0_DB_PATH: first.path },
    });
    assert.equal(backupHealth.status, 0, backupHealth.stderr || backupHealth.stdout);
    const restored = JSON.parse(backupHealth.stdout);
    assert.equal(restored.integrity, "ok");
    assert.equal(restored.counts.candidates, 1);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});

test("backup wrapperは共通DB toolを使い、JSON証跡を返す", async () => {
  const wrapper = await readFile(join(webRoot, "backup.ps1"), "utf8");
  assert.match(wrapper, /db_tool\.py/);
  assert.match(wrapper, /backup-database/);
  assert.match(wrapper, /P0_BACKUP_DIR/);
  assert.doesNotMatch(wrapper, /Remove-Item/);
});

test("healthは設定済み依存へ到達できない時も短時間でdegradedを返す", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-health-degraded-"));
  const appPort = 4194;
  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(appPort),
      P0_DB_PATH: join(dir, "p0.sqlite"),
      VIKUNJA_BASE_URL: "http://127.0.0.1:9",
      VIKUNJA_PUBLIC_URL: "http://127.0.0.1:9",
      VIKUNJA_PROJECT_ID: "1",
      VIKUNJA_API_TOKEN: "health-test-token",
      LOCAL_LLM_ENABLED: "true",
      LOCAL_LLM_BASE_URL: "http://127.0.0.1:9/v1",
      HEALTH_DEPENDENCY_TIMEOUT_MS: "250",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await rm(dir, { recursive: true, force: true });
  });
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  const startedAt = performance.now();
  const response = await fetch(`http://127.0.0.1:${appPort}/api/health`);
  const health = await response.json();
  assert.equal(response.status, 200);
  assert.equal(health.status, "degraded");
  assert.equal(health.database.status, "ok");
  assert.equal(health.dependencies.vikunja.status, "unavailable");
  assert.equal(health.dependencies.localLlm.status, "unavailable");
  assert.ok(performance.now() - startedAt < 2000);
  assert.equal(JSON.stringify(health).includes("health-test-token"), false);
});

test("ローカルLLM相談は会話を保存し、候補を確認待ちへ追加できる", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-chat-api-"));
  const appPort = 4191;
  const llmPort = 4290;
  const received = [];
  const fakeLlm = createServer(async (request, response) => {
    let body = "";
    for await (const chunk of request) body += chunk;
    if (request.method === "POST" && request.url === "/api/show") {
      response.writeHead(200, { "content-type": "application/json" });
      response.end(JSON.stringify({ model_info: { "test-model.context_length": 32768 } }));
      return;
    }
    if (request.method !== "POST" || request.url !== "/v1/chat/completions") {
      response.writeHead(404, { "content-type": "application/json" });
      response.end(JSON.stringify({ error: "not found" }));
      return;
    }
    received.push(JSON.parse(body));
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({
      choices: [{
        message: {
          role: "assistant",
          content: [
            "相談内容を整理しました。タスク候補にしますか？",
            "THREADLINE_TASK_PROPOSALS",
            "```json",
            JSON.stringify([{
              title: "相談からのタスク",
              summary: "相談内容を実装候補として整理する",
              todo: "相談からのタスクを確認待ちキューで確認する",
              kind: "todo",
              schedule: "候補なし",
              confidence: "medium",
              missing: [],
            }]),
            "```",
            "END_THREADLINE_TASK_PROPOSALS",
          ].join("\n"),
        },
      }],
    }));
  });
  await new Promise((resolve) => fakeLlm.listen(llmPort, "127.0.0.1", resolve));

  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(appPort),
      P0_DB_PATH: join(dir, "p0.sqlite"),
      LOCAL_LLM_BASE_URL: `http://127.0.0.1:${llmPort}/v1`,
      LOCAL_LLM_PROVIDER: "ollama",
      LOCAL_LLM_MODEL: "test-model",
      LOCAL_LLM_ENABLE_TOOLS: "false",
      VIKUNJA_BASE_URL: "",
      VIKUNJA_PROJECT_ID: "",
      VIKUNJA_API_TOKEN: "",
      VIKUNJA_PUBLIC_URL: "",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await new Promise((resolve) => fakeLlm.close(resolve));
    await rm(dir, { recursive: true, force: true });
  });

  const localRequest = async (path, options = {}) => {
    const response = await fetch(`http://127.0.0.1:${appPort}${path}`, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.text();
    assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
    return JSON.parse(body);
  };
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  const initial = await localRequest("/api/chat/bootstrap");
  assert.equal(initial.thread.id, "chat-default");
  assert.equal(initial.config.model, "test-model");
  assert.equal(initial.config.contextLength, 32768);
  assert.equal(Object.hasOwn(initial.config, "apiKey"), false);
  assert.equal(initial.context.vikunja.available, false);

  const response = await localRequest("/api/chat/messages", {
    method: "POST",
    body: JSON.stringify({ threadId: "chat-default", content: "この相談を実装タスクとして整理したい" }),
  });
  assert.equal(response.suggestions.length, 1);
  assert.doesNotMatch(response.assistantMessage.content, /THREADLINE_TASK_PROPOSALS/);
  assert.equal(response.suggestions[0].status, "proposed");
  assert.equal(received.length, 1);
  assert.equal(received[0].think, false);
  assert.match(received[0].messages.find((message) => message.role === "system").content, /Threadline context/);
  assert.match(received[0].messages.find((message) => message.role === "system").content, /要約は入力にない推測や定型の導入句を入れない/);
  assert.match(received[0].messages.find((message) => message.role === "system").content, /todoは画面でそのまま実行タイトルとして読める具体的な行動句/);
  assert.equal(received[0].messages.at(-1).content, "この相談を実装タスクとして整理したい");

  const accepted = await localRequest(`/api/chat/suggestions/${encodeURIComponent(response.suggestions[0].id)}/accept`, {
    method: "POST",
    body: "{}",
  });
  assert.equal(accepted.candidate.status, "pending");
  assert.equal(accepted.candidate.source, "chat");
  assert.equal(accepted.candidate.summary, "相談内容を実装候補として整理する");

  const persisted = await localRequest("/api/chat/bootstrap");
  assert.equal(persisted.messages.length, 2);
  assert.equal(persisted.suggestions[0].status, "candidate_pending");
  const hub = await localRequest("/api/bootstrap");
  assert.equal(hub.sources.some((source) => source.id === "chat"), true);
  assert.equal(hub.candidates.some((candidate) => candidate.id === accepted.candidate.id && candidate.source === "chat"), true);
});

test("ローカルLLMエージェントのcontext toolは指定scopeだけを読み取り、回答生成を継続する", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-chat-tool-api-"));
  const appPort = 4192;
  const llmPort = 4291;
  const received = [];
  const fakeLlm = createServer(async (request, response) => {
    let body = "";
    for await (const chunk of request) body += chunk;
    if (request.method !== "POST" || request.url !== "/v1/chat/completions") {
      response.writeHead(404, { "content-type": "application/json" });
      response.end(JSON.stringify({ error: "not found" }));
      return;
    }
    const payload = JSON.parse(body);
    received.push(payload);
    response.writeHead(200, { "content-type": "application/json" });
    if (received.length === 1) {
      response.end(JSON.stringify({
        choices: [{
          message: {
            role: "assistant",
            content: null,
            tool_calls: [{
              id: "call-context-1",
              type: "function",
              function: {
                name: "get_threadline_context",
                arguments: JSON.stringify({ scope: "tasks" }),
              },
            }],
          },
        }],
      }));
      return;
    }
    response.end(JSON.stringify({
      choices: [{ message: { role: "assistant", content: "現在のTasks状況を確認しました。" } }],
    }));
  });
  await new Promise((resolve) => fakeLlm.listen(llmPort, "127.0.0.1", resolve));

  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(appPort),
      P0_DB_PATH: join(dir, "p0.sqlite"),
      LOCAL_LLM_BASE_URL: `http://127.0.0.1:${llmPort}/v1`,
      LOCAL_LLM_MODEL: "tool-test-model",
      LOCAL_LLM_ENABLE_TOOLS: "true",
      VIKUNJA_BASE_URL: "",
      VIKUNJA_PROJECT_ID: "",
      VIKUNJA_API_TOKEN: "",
      VIKUNJA_PUBLIC_URL: "",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await new Promise((resolve) => fakeLlm.close(resolve));
    await rm(dir, { recursive: true, force: true });
  });

  const localRequest = async (path, options = {}) => {
    const response = await fetch(`http://127.0.0.1:${appPort}${path}`, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.text();
    assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
    return JSON.parse(body);
  };
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  const result = await localRequest("/api/chat/messages", {
    method: "POST",
    body: JSON.stringify({ threadId: "chat-default", content: "今のタスク状況を見て" }),
  });
  assert.equal(result.assistantMessage.content, "現在のTasks状況を確認しました。");
  assert.equal(received.length, 2);
  assert.equal(received[0].tools[0].function.name, "get_threadline_context");
  const toolMessage = received[1].messages.find((message) => message.role === "tool");
  assert.ok(toolMessage);
  const scopedContext = JSON.parse(toolMessage.content);
  assert.ok(Object.hasOwn(scopedContext, "vikunja"));
  assert.ok(Object.hasOwn(scopedContext, "execution_state"));
  assert.equal(Object.hasOwn(scopedContext, "hub"), false);
});

test("GOは実Vikunja契約でtaskを1件だけ作り、署名付きWebhookを反映する", async (context) => {
  const dir = await mkdtemp(join(tmpdir(), "pj-general-vikunja-api-"));
  const appPort = 4188;
  const vikunjaPort = 4289;
  const webhookSecret = "integration-test-webhook-secret";
  const received = [];
  let fakeTask = null;
  const fakeVikunja = createServer(async (request, response) => {
    let body = "";
    for await (const chunk of request) body += chunk;
    if (request.method === "PUT" && request.url === "/api/v1/projects/1/tasks") {
      const parsed = JSON.parse(body);
      received.push({ method: request.method, url: request.url, authorization: request.headers.authorization, body: parsed });
      fakeTask = { id: 77, title: parsed.title, done: false, priority: 0, percent_done: 0 };
      response.writeHead(201, { "content-type": "application/json" });
      response.end(JSON.stringify(fakeTask));
      return;
    }
    if (request.method === "GET" && request.url === "/api/v1/projects/1") {
      response.writeHead(200, { "content-type": "application/json" });
      response.end(JSON.stringify({ id: 1, title: "Inbox" }));
      return;
    }
    if (request.method === "GET" && request.url === "/api/v1/projects/1/tasks") {
      response.writeHead(200, { "content-type": "application/json" });
      response.end(JSON.stringify(fakeTask ? [{ ...fakeTask, due_date: "2026-07-20T12:00:00Z", updated: "2026-07-11T12:00:00Z" }] : []));
      return;
    }
    if (request.method === "GET" && request.url === "/api/v1/tasks/77") {
      if (!fakeTask) {
        response.writeHead(404, { "content-type": "application/json" });
        response.end(JSON.stringify({ message: "task not found" }));
        return;
      }
      response.writeHead(200, { "content-type": "application/json" });
      response.end(JSON.stringify(fakeTask));
      return;
    }
    response.writeHead(404, { "content-type": "application/json" });
    response.end(JSON.stringify({ message: "not found" }));
  });
  await new Promise((resolve) => fakeVikunja.listen(vikunjaPort, "127.0.0.1", resolve));

  const child = spawn(process.execPath, [join(webRoot, "server.mjs")], {
    cwd: webRoot,
    env: {
      ...process.env,
      PORT: String(appPort),
      P0_DB_PATH: join(dir, "p0.sqlite"),
      VIKUNJA_BASE_URL: `http://127.0.0.1:${vikunjaPort}`,
      VIKUNJA_API_BASE_PATH: "/api/v1",
      VIKUNJA_PROJECT_ID: "1",
      VIKUNJA_API_TOKEN: "test-token",
      VIKUNJA_WEBHOOK_SECRET: webhookSecret,
      LOCAL_LLM_ENABLED: "false",
    },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await new Promise((resolve) => fakeVikunja.close(resolve));
    await rm(dir, { recursive: true, force: true });
  });

  const localRequest = async (path, options = {}) => {
    const response = await fetch(`http://127.0.0.1:${appPort}${path}`, {
      headers: { "content-type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.text();
    assert.ok(response.ok, `${options.method || "GET"} ${path} failed: ${body}`);
    return JSON.parse(body);
  };
  for (let index = 0; index < 30; index += 1) {
    try {
      if ((await fetch(`http://127.0.0.1:${appPort}/api/bootstrap`)).ok) break;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  const candidate = await localRequest("/api/candidates", {
    method: "POST",
    body: JSON.stringify({ title: "実Vikunja結合を確認する", summary: "P0結合候補", todo: "taskを作る" }),
  });
  const first = await localRequest(`/api/candidates/${candidate.id}/execution`, {
    method: "POST",
    body: JSON.stringify({ operation_id: "p0-u03-go" }),
  });
  const second = await localRequest(`/api/candidates/${candidate.id}/execution`, { method: "POST", body: "{}" });
  assert.equal(first.external_task_id, "77");
  assert.equal(first.operation_id, "p0-u03-go");
  assert.equal(second.external_task_id, "77");
  assert.equal(received.length, 1);
  assert.equal(received[0].method, "PUT");
  assert.equal(received[0].url, "/api/v1/projects/1/tasks");
  assert.equal(received[0].authorization, "Bearer test-token");
  assert.equal(received[0].body.title, "taskを作る");

  const overview = await localRequest("/api/integrations/vikunja/overview");
  assert.equal(overview.available, true);
  assert.deepEqual(overview.project, {
    id: 1,
    title: "Inbox",
    url: `http://127.0.0.1:${vikunjaPort}/projects/1`,
  });
  assert.deepEqual(overview.summary, { total: 1, open: 1, done: 0 });
  assert.equal(overview.tasks[0].title, "taskを作る");
  assert.equal(JSON.stringify(overview).includes("test-token"), false);
  const health = await localRequest("/api/health");
  assert.equal(health.status, "ok");
  assert.equal(health.dependencies.vikunja.status, "ok");
  assert.equal(health.dependencies.localLlm.status, "disabled");
  assert.equal(JSON.stringify(health).includes("test-token"), false);

  const webhookBody = JSON.stringify({ event_name: "task.updated", data: { task: { id: 77, title: "実Vikunja結合を確認する", done: true, priority: 3, percent_done: 100 } } });
  const signature = createHmac("sha256", webhookSecret).update(webhookBody).digest("hex");
  await localRequest("/api/integrations/vikunja/webhook", {
    method: "POST",
    headers: { "x-vikunja-signature": signature },
    body: webhookBody,
  });
  await localRequest("/api/integrations/vikunja/webhook", {
    method: "POST",
    headers: { "x-vikunja-signature": signature },
    body: webhookBody,
  });
  const invalidWebhook = await fetch(`http://127.0.0.1:${appPort}/api/integrations/vikunja/webhook`, {
    method: "POST",
    headers: { "content-type": "application/json", "x-vikunja-signature": "invalid" },
    body: webhookBody,
  });
  assert.equal(invalidWebhook.status, 401);
  const bootstrap = await localRequest("/api/bootstrap");
  assert.equal(bootstrap.log.find((item) => item.title === candidate.todo && item.action === "approved").operationId, "p0-u03-go");
  assert.equal(bootstrap.executionLinks.find((item) => item.candidate_id === candidate.id).sync_state, "synced");
  assert.equal(bootstrap.executionTaskStates.find((item) => item.candidate_id === candidate.id).done, 1);
  assert.equal(bootstrap.syncEvents.length, 1);

  fakeTask = { ...fakeTask, done: false, priority: 5, percent_done: 50 };
  const reconciled = await localRequest("/api/integrations/vikunja/reconcile", { method: "POST", body: "{}" });
  assert.deepEqual(reconciled, { checked: 1, updated: 1, detached: 0, failed: 0 });
  const afterReconcile = await localRequest("/api/bootstrap");
  assert.equal(afterReconcile.executionTaskStates.find((item) => item.candidate_id === candidate.id).priority, 5);

  fakeTask = null;
  const detached = await localRequest("/api/integrations/vikunja/reconcile", { method: "POST", body: "{}" });
  assert.deepEqual(detached, { checked: 1, updated: 0, detached: 1, failed: 0 });
  const afterDelete = await localRequest("/api/bootstrap");
  assert.equal(afterDelete.executionLinks.find((item) => item.candidate_id === candidate.id).sync_state, "detached");
});

test("クライアントはSQLite応答失敗時に仮候補を作らない", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  assert.equal(app.includes("structuredClone(candidates)"), false);
  assert.equal(app.includes("candidate = {\n      id: `AI-"), false);
  assert.match(app, /navigator\.clipboard\.writeText/);
  assert.match(app, /\/execution/);
  assert.match(app, /Tasks側で開く/);
  assert.match(app, /integrations\/vikunja\/overview/);
  assert.match(app, /function displayCandidateTitle\(candidate\)/);
});

test("実データを変更する候補判断は画面上の確認を経てから送信する", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");

  assert.match(app, /function confirmCandidateAction\(status\)/);
  assert.match(app, /window\.confirm\(/);
  assert.match(app, /confirmCandidateAction\(status\)/);
  assert.match(app, /payload\.status === "approved" && !confirmCandidateAction\("approved"\)/);
  assert.match(app, /function createOperationId\(action\)/);
  assert.match(app, /操作ID/);
  assert.match(app, /HTTP \$\{[^}]+\}/);
});

test("候補判断後はobservability取得失敗でもbootstrapの判断ログを表示できる", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  const start = app.indexOf("async function refreshBootstrap");
  const end = app.indexOf("async function addManualCandidate", start);
  const refresh = app.slice(start, end);

  assert.match(refresh, /const bootstrap = await apiJson\("\/api\/bootstrap"\)/);
  assert.match(refresh, /state\.observability = await apiJson\("\/api\/observability"\)/);
  assert.match(refresh, /catch \(error\) \{[\s\S]*state\.observability/);
});

test("Linuxコンテナではbind先とSQLiteを環境変数で切り替えられる", async () => {
  const server = await readFile(join(webRoot, "server.mjs"), "utf8");
  const dockerfile = await readFile(join(webRoot, "Dockerfile"), "utf8");
  assert.match(server, /process\.env\.HOST \|\| "127\.0\.0\.1"/);
  assert.match(dockerfile, /P0_DB_PATH=\/data\/p0\.sqlite/);
  assert.match(dockerfile, /PYTHON=python3/);
});

test("入口別の量はSQLiteの全入口を0件でも描画対象にする", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  assert.match(app, /sourceSettings\.map/);
  assert.match(app, /source\.id/);
});

test("候補の種類はSQLiteに存在しない種類も0件で描画対象にする", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  assert.match(app, /kindDisplayOrder/);
  assert.match(app, /count = counts\[kind\] \|\| 0/);
});

test("Hubの入口別・種類別は固定高にし、Tasks導線とデバッグ表示を明確にする", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const theme = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.match(theme, /dashboard-source \.source-list,[\s\S]*dashboard-kinds \.source-list[\s\S]*block-size:\s*340px/);
  assert.match(theme, /dashboard-source \.source-list,[\s\S]*dashboard-kinds \.source-list[\s\S]*min-block-size:\s*0/);
  assert.match(theme, /dashboard-source,[\s\S]*dashboard-kinds[\s\S]*min-height:\s*0 !important/);
  assert.match(html, /class="[^"]*tasks-primary-link[^"]*"[^>]*id="tasksOpenLink"/);
  assert.match(theme, /\.tasks-primary-link:not\(\.is-disabled\)\s*\{[\s\S]*background:\s*#5176d8/);
  assert.match(html, /class="sidebar-note debug-note"/);
  assert.match(theme, /\.debug-note,[\s\S]*\.admin-status,[\s\S]*\.observability-status/);
});

test("管理カードは状態をタイトル横、操作を縦積みで示す", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  const css = await readFile(join(webRoot, "styles.css"), "utf8");
  const html = await readFile(join(webRoot, "index.html"), "utf8");

  assert.match(app, /class="admin-control-heading"/);
  assert.match(app, /class="control-state \$\{item\.enabled \? "control-state--enabled" : "control-state--disabled"\}"/);
  assert.match(app, /item\.enabled \? "有効" : "停止中"/);
  assert.match(app, /item\.enabled \? "無効化" : "有効化"/);
  assert.match(app, /data-admin-action="\$\{item\.action\}">取込<\/button>/);
  assert.match(css, /\.admin-buttons\s*\{[\s\S]*flex-direction:\s*column/);
  assert.match(css, /\.admin-grid\s*\{[\s\S]*grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\)/);
  assert.ok(html.indexOf("入口設定") < html.indexOf("タグマスタ"));
  assert.ok(html.indexOf("タグマスタ") < html.indexOf("プロンプトテンプレート"));
  assert.ok(html.indexOf("プロンプトテンプレート") < html.indexOf("取り込み対象"));
  assert.ok(html.indexOf("取り込み対象") < html.indexOf("ロール表示"));
  assert.ok(html.indexOf("ロール表示") < html.indexOf("AI確定方針"));
});

test("横断ダッシュボードは処理フローと3列の要約を画像指定どおりに配置する", async () => {
  const css = await readFile(join(webRoot, "styles.css"), "utf8");
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  assert.match(css, /grid-template-areas:\s*"flow flow tasks"\s*"sources kinds attention"\s*"sources kinds decisions"/);
  assert.match(css, /grid-template-columns: minmax\(0, 1fr\) minmax\(0, 1fr\) minmax\(0, 2fr\)/);
  assert.match(html, /dashboard-source/);
  assert.match(html, /dashboard-kinds/);
  assert.match(html, /tasksOpenLink/);
});

test("Hub左レールは運用の読み順に合わせ、AI相談と詳細管理を独立したサイド操作にする", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");

  assert.match(html, /href="#dashboard"[^>]*>ダッシュボード<\/a>/);
  assert.match(html, /href="#gantt"[^>]*>簡易日程<\/a>/);
  assert.match(html, /href="#queue"[^>]*>タスクキュー<\/a>/);
  assert.match(html, /href="#worker"[^>]*>ワークビュー<\/a>/);
  assert.match(html, /href="#admin"[^>]*>簡易管理<\/a>/);
  assert.doesNotMatch(html, /href="\/chat"[^>]*>相談<\/a>/);
  assert.match(html, /id="dashboard-title">ダッシュボード<\/h2>/);
  assert.match(html, /id="gantt-title">簡易日程<\/h2>/);
  assert.match(html, /id="queue-title">タスクキュー<\/h2>/);
  assert.match(html, /id="worker-title">ワークビュー<\/h2>/);
  assert.match(html, /id="admin-title">簡易管理<\/h2>/);
  assert.match(html, /data-open-chat[\s\S]*AI相談/);
  assert.match(html, /class="nav-side-chat[^\"]*is-disabled[^\"]*"[^>]*aria-disabled="true"[\s\S]*詳細管理/);
});

test("Hub左レールのハッシュ遷移は各セクションのscroll marginを尊重する", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  const theme = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.match(html, /href="#dashboard"/);
  assert.match(html, /href="#gantt"/);
  assert.match(html, /href="#queue"/);
  assert.match(html, /href="#worker"/);
  assert.match(html, /href="#admin"/);
  assert.match(theme, /\.section,[\s\S]*\.summary-grid[\s\S]*scroll-margin-top:\s*20px/);
  assert.match(app, /function scrollToSection\(target, behavior\) \{[\s\S]*target\.scrollIntoView\(\{ behavior, block: "start" \}\)/);
  assert.match(app, /scrollToSection\(target, "auto"\)/);
});

test("P0受入チェックはR06/R07を定常作業として最上段に固定し、未配信時は赤へ戻せる", async () => {
  const checklist = await readFile(join(webRoot, "../../docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html"), "utf8");

  assert.match(checklist, /定常作業[\s\S]*配信状態と実機反映/);
  assert.ok(checklist.indexOf("{id:'R06'") < checklist.indexOf("{id:'RV01'"));
  assert.ok(checklist.indexOf("{id:'R07'") < checklist.indexOf("{id:'RV01'"));
  assert.match(checklist, /row\.result==='failed'\?'blocked':task\.level/);
  assert.match(checklist, /R06\/R07は再配信済みの定常作業/);
});

test("確認待ちキューのフィルターは固定幅で左寄せにする", async () => {
  const css = await readFile(join(webRoot, "styles.css"), "utf8");
  assert.match(css, /\.queue-tools\s*\{[\s\S]*grid-template-columns: repeat\(4, minmax\(220px, 255px\)\)/);
  assert.match(css, /\.queue-tools\s*\{[\s\S]*justify-content: start/);
});

test("画面セクションの主要列は利用可能幅を比率で分配する", async () => {
  const css = await readFile(join(webRoot, "styles.css"), "utf8");
  assert.match(css, /\.worker-grid\s*\{[\s\S]*grid-template-columns: minmax\(0, 11fr\) minmax\(0, 9fr\)/);
  assert.match(css, /\.queue-layout\s*\{[\s\S]*grid-template-columns: minmax\(0, 1fr\) minmax\(0, 2fr\)/);
  assert.match(css, /\.detail-pane\s*\{[\s\S]*min-width: 0/);
});

test("Listening Loungeを本流テーマとして配信する", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const server = await readFile(join(webRoot, "server.mjs"), "utf8");
  const theme = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.match(html, /data-theme="listening-lounge"/);
  assert.match(html, /listening-lounge\.css/);
  assert.match(html, /room-atmosphere/);
  assert.doesNotMatch(html, /theme-lab-switcher/);
  assert.doesNotMatch(server, /renderThemePreview/);
  assert.match(server, /theme-room-03/);
  assert.match(server, /location:\s*"\/"/);
  assert.match(theme, /--room-signature:\s*listening-lounge/);
  assert.doesNotMatch(theme, /data-theme-preview/);
});

test("Hub左レールは正式な縮小TLモノグラムを使う", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const theme = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.match(html, /class="brand-mark"[\s\S]*thread-line-mark-master-256\.png/);
  assert.match(html, /alt="TL"/);
  assert.match(theme, /\.brand-mark-image\s*\{[\s\S]*object-fit:\s*cover/);
  assert.match(theme, /\.brand-mark\s*\{[\s\S]*width:\s*44px[\s\S]*height:\s*44px/);
});

test("Hub左レールはThread Line Hubの薄橙識別だけを表示する", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const theme = await readFile(join(webRoot, "listening-lounge.css"), "utf8");

  assert.match(html, /class="brand-copy">[\s\S]*Thread Line Hub/);
  assert.doesNotMatch(html, /P0 試作/);
  assert.match(theme, /\.brand-copy\s*\{[\s\S]*background:\s*#3d302d/);
});

test("HubとTasks側の編集責務、未接続時の次操作、mirror状態を画面へ出す", async () => {
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  const app = await readFile(join(webRoot, "app.js"), "utf8");

  assert.match(html, /Hubで編集/);
  assert.match(html, /Tasks側で編集/);
  assert.match(html, /data-task-responsibility/);
  assert.match(app, /Vikunjaは未接続です。設定後に更新してください。/);
  assert.match(app, /Vikunjaへ接続できません。更新して再試行してください。/);
  assert.match(app, /executionTaskStates/);
  assert.match(app, /状態mirror/);
  assert.doesNotMatch(app, /setVikunjaLink\("tasksNavLink"/);
});

test("Hubは最新の判断ログをDB順で表示し、初回ガントを再レイアウトする", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");

  assert.match(app, /const log = state\.log\.slice\(0, 5\)/);
  assert.doesNotMatch(app, /state\.log\.slice\(-5\)\.reverse\(\)/);
  assert.match(app, /visibilitychange/);
  assert.match(app, /requestAnimationFrame\(\(\) => \{[\s\S]*renderGantt\(\)/);
});

test("完成度星取表は進行中の工程・現在のブロッカー・次の作業を表示する", async () => {
  const scorecard = await readFile(join(webRoot, "..", "..", "docs", "imp", "p0-p1-completion-assessment-2026-07-12.html"), "utf8");

  assert.match(scorecard, /現在の作業/);
  assert.match(scorecard, /Hub候補・判断フローの実画面受入/);
  assert.match(scorecard, /定常R06\/R07/);
  assert.match(scorecard, /定常R06\/R07を赤から実行する/);
  assert.match(scorecard, /P0本体も未受入のUI\/UX・連携・安全を満点にしない/);
  assert.match(scorecard, /Hub左レールはダッシュボード／簡易日程／タスクキュー／ワークビュー／簡易管理へ再編/);
  assert.match(scorecard, /U03は判断ログを操作IDで照合する実データ受入/);
  assert.match(scorecard, /次の作業/);
  assert.match(scorecard, /scorecard-current-work/);
});

test("完成度星取表は直接の5段階評価、列見出しの軸名、ブロック背景を使う", async () => {
  const scorecard = await readFile(join(webRoot, "..", "..", "docs", "imp", "p0-p1-completion-assessment-2026-07-12.html"), "utf8");

  assert.match(scorecard, /R 要件/);
  assert.match(scorecard, /I 実装/);
  assert.match(scorecard, /S 安全/);
  assert.match(scorecard, /評価値そのものを0〜5の五段階で記録/);
  assert.match(scorecard, /function fivePointScore\(score\) \{ return score; \}/);
  assert.doesNotMatch(scorecard, /Math\.floor\(score \/ 2\)/);
  assert.match(scorecard, /for \(let n = 1; n <= 5; n \+= 1\)/);
  assert.match(scorecard, /task\.blocked/);
  assert.match(scorecard, /\.blocked-row/);
});

test("P0受入チェック表は赤黄の手順、結果コメント、報告プロンプトを備える", async () => {
  const checklist = await readFile(join(webRoot, "..", "..", "docs", "imp", "p0-frontend-acceptance-checklist-2026-07-12.html"), "utf8");

  assert.match(checklist, /Listening Lounge/);
  assert.match(checklist, /ブロック/);
  assert.match(checklist, /要確認/);
  assert.match(checklist, /完了/);
  assert.match(checklist, /未達/);
  assert.match(checklist, /E902…544Fのfork sourceをLinuxでrebuild/);
  assert.match(checklist, /1280px task detailで、右操作railが本文下の操作面へ移る/);
  assert.match(checklist, /再受入JPEG一覧/);
  assert.match(checklist, /project-dashboard01-before\.jpg/);
  assert.match(checklist, /project-gantt09-after\.jpg/);
  assert.match(checklist, /R03/);
  assert.match(checklist, /B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9/);
  assert.match(checklist, /R04/);
  assert.match(checklist, /Thread Line・RV01〜RV04・U03操作IDをLinuxへ再反映/);
  assert.match(checklist, /R05/);
  assert.match(checklist, /R06/);
  assert.match(checklist, /定常作業 \/ 配信状態と実機反映/);
  assert.match(checklist, /R06\/R07は再配信済みの定常作業/);
  assert.match(checklist, /Kanban guide修正・Thread Line左レール比較を実機受入/);
  const scriptStart = checklist.indexOf("<script>") + "<script>".length;
  const scriptEnd = checklist.indexOf("</script>", scriptStart);
  assert.doesNotThrow(() => new Function(checklist.slice(scriptStart, scriptEnd)));
  assert.match(checklist, /コメント/);
  assert.match(checklist, /報告プロンプトを生成/);
  assert.match(checklist, /localStorage/);
  assert.match(checklist, /textarea/);
  assert.match(checklist, /defaultState/);
  assert.match(checklist, /A02/);
});
