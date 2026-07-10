import assert from "node:assert/strict";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { spawn } from "node:child_process";

const require = createRequire(import.meta.url);
const webRoot = join(import.meta.dirname, "..");
const port = 4187;
const baseUrl = `http://127.0.0.1:${port}`;

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

test("クライアントはSQLite応答失敗時に仮候補を作らない", async () => {
  const app = await readFile(join(webRoot, "app.js"), "utf8");
  assert.equal(app.includes("structuredClone(candidates)"), false);
  assert.equal(app.includes("candidate = {\n      id: `AI-"), false);
  assert.match(app, /navigator\.clipboard\.writeText/);
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
  assert.match(css, /grid-template-areas:\s*"flow flow empty"\s*"sources kinds attention"\s*"sources kinds decisions"/);
  assert.match(css, /grid-template-columns: minmax\(0, 1fr\) minmax\(0, 1fr\) minmax\(0, 2fr\)/);
  assert.match(html, /dashboard-source/);
  assert.match(html, /dashboard-kinds/);
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
