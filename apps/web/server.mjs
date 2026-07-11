import { createReadStream, existsSync, statSync } from "node:fs";
import { createHmac, timingSafeEqual } from "node:crypto";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const port = Number.parseInt(process.env.PORT || "4173", 10);
const host = process.env.HOST || "127.0.0.1";
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

function verifyVikunjaSignature(rawBody, signature, secret) {
  if (!signature || !secret) return false;
  const expected = createHmac("sha256", secret).update(rawBody).digest("hex");
  if (signature.length !== expected.length) return false;
  return timingSafeEqual(Buffer.from(signature, "utf8"), Buffer.from(expected, "utf8"));
}

async function createVikunjaExecution(candidateId) {
  const prepared = runDb("prepare-execution", { id: candidateId });
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
        body: JSON.stringify({ title: candidate.title, description }),
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
  const config = vikunjaConfig();
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
  return summary;
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
    const executionMatch = url.pathname.match(/^\/api\/candidates\/([^/]+)\/execution$/);
    if (request.method === "POST" && executionMatch) {
      const candidateId = decodeURIComponent(executionMatch[1]);
      const link = await createVikunjaExecution(candidateId);
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
}).listen(port, host, () => {
  console.log(`pj-general web: http://${host}:${port}`);
});
