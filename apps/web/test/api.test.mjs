import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
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
    env: { ...process.env, PORT: String(port), P0_DB_PATH: join(dir, "p0.sqlite") },
    stdio: "ignore",
  });
  context.after(async () => {
    child.kill();
    await rm(dir, { recursive: true, force: true });
  });

  await waitForServer();
  const initial = await request("/api/bootstrap");
  assert.equal(initial.candidates.some((candidate) => /mock/i.test(JSON.stringify(candidate))), false);
  assert.ok(Array.isArray(initial.adminControls.roles));
  assert.ok(Array.isArray(initial.adminControls.automation));
  assert.ok(Array.isArray(initial.adminControls.scopes));

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
      ["execution_links", "execution_task_state", "sync_attempts", "sync_events"].filter((name) => !schema.tables.includes(name)),
      [],
    );
    assert.ok(schema.uniqueIndexes.sync_events.includes("dedupe_key"));
    assert.ok(schema.uniqueIndexes.sync_attempts.includes("idempotency_key"));
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
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
  const first = await localRequest(`/api/candidates/${candidate.id}/execution`, { method: "POST", body: "{}" });
  const second = await localRequest(`/api/candidates/${candidate.id}/execution`, { method: "POST", body: "{}" });
  assert.equal(first.external_task_id, "77");
  assert.equal(second.external_task_id, "77");
  assert.equal(received.length, 1);
  assert.equal(received[0].method, "PUT");
  assert.equal(received[0].url, "/api/v1/projects/1/tasks");
  assert.equal(received[0].authorization, "Bearer test-token");

  const overview = await localRequest("/api/integrations/vikunja/overview");
  assert.equal(overview.available, true);
  assert.deepEqual(overview.project, {
    id: 1,
    title: "Inbox",
    url: `http://127.0.0.1:${vikunjaPort}/projects/1`,
  });
  assert.deepEqual(overview.summary, { total: 1, open: 1, done: 0 });
  assert.equal(overview.tasks[0].title, "実Vikunja結合を確認する");
  assert.equal(JSON.stringify(overview).includes("test-token"), false);

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

test("横断ダッシュボードは処理フローと3列の要約を画像指定どおりに配置する", async () => {
  const css = await readFile(join(webRoot, "styles.css"), "utf8");
  const html = await readFile(join(webRoot, "index.html"), "utf8");
  assert.match(css, /grid-template-areas:\s*"flow flow tasks"\s*"sources kinds attention"\s*"sources kinds decisions"/);
  assert.match(css, /grid-template-columns: minmax\(0, 1fr\) minmax\(0, 1fr\) minmax\(0, 2fr\)/);
  assert.match(html, /dashboard-source/);
  assert.match(html, /dashboard-kinds/);
  assert.match(html, /tasksOpenLink/);
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
