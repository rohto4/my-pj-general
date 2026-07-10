import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const port = Number.parseInt(process.env.PORT || "4173", 10);
const dbTool = join(root, "db_tool.py");
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

async function handleApi(request, response, url) {
  try {
    if (request.method === "GET" && url.pathname === "/api/bootstrap") {
      sendJson(response, 200, runDb("bootstrap"));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/candidates") {
      const body = await readBody(request);
      sendJson(response, 201, runDb("create-candidate", JSON.parse(body || "{}")));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/import/knowledge-vault") {
      const body = await readBody(request);
      sendJson(response, 200, runDb("import-knowledge-vault", JSON.parse(body || "{}")));
      return true;
    }
    if (request.method === "POST" && url.pathname === "/api/import/slack") {
      const body = await readBody(request);
      sendJson(response, 200, runDb("import-slack", JSON.parse(body || "{}")));
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
    sendJson(response, 500, { error: error.message });
    return true;
  }
}

runDb("bootstrap");

createServer(async (request, response) => {
  const url = new URL(request.url || "/", `http://localhost:${port}`);
  if (url.pathname.startsWith("/api/") && (await handleApi(request, response, url))) {
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
}).listen(port, "127.0.0.1", () => {
  console.log(`pj-general web prototype: http://127.0.0.1:${port}`);
});
