let ganttTasks = [];
let weekScale = [];
const ganttWindowDays = 28;
let ganttWindowStart = null;

let tagMaster = [];
let sourceSettings = [];
let promptSettings = [];
const adminSettings = { roles: [], automation: [], scopes: [] };

const state = {
  candidates: [],
  selectedId: "",
  log: [],
  executionLinks: [],
  executionTaskStates: [],
  vikunjaOverview: { available: false, reason: "loading", project: null, tasks: [], summary: { total: 0, open: 0, done: 0 } },
  chat: {
    threadId: "chat-default",
    messages: [],
    suggestions: [],
    context: null,
    config: null,
    loading: false,
    initialized: false,
  },
  dbPath: "",
  editingId: "",
  adminNotice: "SQLite を読み込み中",
  observability: null,
};

const options = {
  status: ["all", "pending", "edited", "approved", "rejected", "archived"],
  source: ["all", "web", "slack", "misskey", "knowledge_vault", "chat"],
  kind: ["all", "idea", "consideration", "concern", "todo", "schedule_candidate"],
  missing: ["all", "has_missing", "complete"],
};

const kindDisplayOrder = ["todo", "consideration", "idea", "schedule_candidate", "concern"];

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function parseLocalDateKey(value) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!match) return null;
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  return Number.isNaN(date.getTime()) ? null : date;
}

function dateOrdinal(date) {
  return Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / 86400000;
}

function getGanttWindowStart() {
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const mondayOffset = start.getDay() === 0 ? -6 : 1 - start.getDay();
  start.setDate(start.getDate() + mondayOffset);
  return start;
}

function formatGanttWeekLabel(date) {
  return `${date.getMonth() + 1}/${date.getDate()}週`;
}

function refreshGanttScale() {
  ganttWindowStart = getGanttWindowStart();
  weekScale = Array.from({ length: 4 }, (_, index) => {
    const date = new Date(ganttWindowStart);
    date.setDate(date.getDate() + index * 7);
    return { label: formatGanttWeekLabel(date), left: (index * 7 / ganttWindowDays) * 100 };
  });
}

function layoutGanttTask(task) {
  const startDate = parseLocalDateKey(task.startDate || task.endDate);
  const endDate = parseLocalDateKey(task.endDate || task.startDate);
  if (!startDate || !endDate || !ganttWindowStart) return null;
  const startIndex = dateOrdinal(startDate) - dateOrdinal(ganttWindowStart);
  const endIndex = dateOrdinal(endDate) - dateOrdinal(ganttWindowStart);
  if (endIndex < 0 || startIndex >= ganttWindowDays) return null;
  const visibleStart = Math.max(0, startIndex);
  const visibleEnd = Math.min(ganttWindowDays - 1, endIndex);
  return {
    ...task,
    start: (visibleStart / ganttWindowDays) * 100,
    span: Math.max(((visibleEnd - visibleStart + 1) / ganttWindowDays) * 100, 1.5),
  };
}

function formatVikunjaDate(value) {
  if (!value) return "期限なし";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleDateString("ja-JP", { month: "numeric", day: "numeric" });
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(options.headers || {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `API failed: ${response.status}`);
  }
  if (payload && typeof payload === "object") {
    Object.defineProperty(payload, "__httpStatus", { value: response.status, enumerable: false });
  }
  return payload;
}

function chatRoleLabel(role) {
  return role === "user" ? "あなた" : role === "assistant" ? "ローカルLLM" : "Threadline";
}

function chatSuggestionsForMessage(messageId) {
  return state.chat.suggestions.filter((suggestion) => String(suggestion.message_id) === String(messageId));
}

function renderChatSuggestion(suggestion) {
  const accepted = suggestion.status === "candidate_pending" || suggestion.status === "accepted";
  return `
    <div class="chat-suggestion" data-chat-suggestion="${escapeHtml(suggestion.id)}">
      <strong>${escapeHtml(suggestion.title)}</strong>
      <p>${escapeHtml(suggestion.summary)}</p>
      <p>TODO案: ${escapeHtml(suggestion.todo)}</p>
      ${accepted
        ? `<span class="badge approved">確認待ちへ追加済み${suggestion.candidate_id ? ` / ${escapeHtml(suggestion.candidate_id)}` : ""}</span>`
        : `<button class="secondary-button" type="button" data-accept-chat-suggestion="${escapeHtml(suggestion.id)}">候補として追加</button>`}
    </div>
  `;
}

function renderChatMessages(containerId) {
  const container = byId(containerId);
  if (!container) return;
  if (state.chat.messages.length === 0) {
    container.innerHTML = `
      <div class="chat-empty">
        <span class="chat-empty__mark" aria-hidden="true">⌁</span>
        <div>
          <strong>ここは、仕事になる前の考えを置く場所です。</strong>
          <p>相談内容を入力すると、現在のHub候補とTasks概要を踏まえて回答します。</p>
          <div class="chat-starters" aria-label="相談の書き出し例">
            <button type="button" data-chat-prompt="今抱えている仕事を整理して、今日見るべきものを教えて">今日見るものを整理</button>
            <button type="button" data-chat-prompt="確認待ちの候補を見て、判断の順番を提案して">確認待ちを相談</button>
            <button type="button" data-chat-prompt="やりたいことがあるので、実行できるタスクに分解して">やりたいことを分解</button>
          </div>
        </div>
      </div>`;
    return;
  }
  container.innerHTML = state.chat.messages
    .map((message) => `
      <article class="chat-message chat-message--${escapeHtml(message.role)}">
        <span class="chat-message__role">${escapeHtml(chatRoleLabel(message.role))}</span>
        <p class="chat-message__content">${escapeHtml(message.content)}</p>
        ${chatSuggestionsForMessage(message.id).length
          ? `<div class="chat-suggestion-list">${chatSuggestionsForMessage(message.id).map(renderChatSuggestion).join("")}</div>`
          : ""}
      </article>
    `)
    .join("");
  container.scrollTop = container.scrollHeight;
}

function renderChatContext() {
  const context = state.chat.context;
  const container = byId("chatContextSnapshot");
  if (!container) return;
  if (!context) {
    container.innerHTML = '<div class="dashboard-empty">現在情報を読み込んでいます。</div>';
    return;
  }
  const hub = context.hub || {};
  const vikunja = context.vikunja || {};
  const summary = vikunja.summary || {};
  container.innerHTML = `
    <div class="chat-context-stat"><span>Hub候補</span><strong>${escapeHtml(hub.candidate_count ?? 0)}件</strong></div>
    <div class="chat-context-stat"><span>確認待ち</span><strong>${escapeHtml(hub.pending_count ?? 0)}件</strong></div>
    <div class="chat-context-stat"><span>Tasks未完了</span><strong>${escapeHtml(summary.open ?? 0)}件</strong></div>
    <div class="chat-context-stat"><span>Tasks完了</span><strong>${escapeHtml(summary.done ?? 0)}件</strong></div>
  `;
}

function renderChatState() {
  renderChatMessages("chatPageMessages");
  renderChatMessages("chatDrawerMessages");
  renderChatContext();
  const config = state.chat.config;
  const status = state.chat.loading
    ? "回答生成中"
    : config?.enabled
      ? "ローカル接続済み"
      : "LLM無効";
  ["chatProviderStatus", "chatPageStatus", "chatDrawerStatus"].forEach((id) => {
    const element = byId(id);
    if (element) element.textContent = status;
  });
  const threadMeta = byId("chatThreadMeta");
  if (threadMeta) threadMeta.textContent = `${state.chat.messages.length}件 · ${state.chat.threadId}`;
  const modelMeta = byId("chatModelMeta");
  if (modelMeta) {
    modelMeta.textContent = config?.enabled
      ? `${config.provider || "local"} / ${config.model}`
      : "モデル未接続";
  }
  const contextMeta = byId("chatContextMeta");
  if (contextMeta) {
    const contextLength = Number(config?.contextLength || 0);
    const contextLengthLabel = contextLength > 0
      ? `最大コンテキスト ${contextLength.toLocaleString("ja-JP")} tokens`
      : "コンテキスト長 未取得";
    contextMeta.textContent = `${contextLengthLabel} · Hub候補とTasks概要を参照`;
  }
}

async function refreshChatBootstrap() {
  state.chat.loading = true;
  renderChatState();
  try {
    const result = await apiJson("/api/chat/bootstrap");
    state.chat.threadId = result.thread.id;
    state.chat.messages = result.messages || [];
    state.chat.suggestions = result.suggestions || [];
    state.chat.context = result.context || null;
    state.chat.config = result.config || null;
    state.chat.initialized = true;
  } catch (error) {
    console.warn(error);
    state.chat.config = { enabled: false, model: "接続エラー" };
  } finally {
    state.chat.loading = false;
    renderChatState();
  }
}

async function sendChatMessage(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const input = form.querySelector("textarea[name=content]");
  const content = input?.value.trim() || "";
  if (!content || state.chat.loading) return;
  state.chat.loading = true;
  renderChatState();
  try {
    const result = await apiJson("/api/chat/messages", {
      method: "POST",
      body: JSON.stringify({ threadId: state.chat.threadId, content }),
    });
    state.chat.messages.push(result.userMessage, result.assistantMessage);
    state.chat.suggestions.push(...(result.suggestions || []));
    state.chat.context = result.context || state.chat.context;
    state.chat.config = result.config || state.chat.config;
    input.value = "";
  } catch (error) {
    const message = error.message || "LLM接続に失敗しました";
    state.chat.messages.push({ id: `error-${Date.now()}`, role: "system", content: message });
  } finally {
    state.chat.loading = false;
    renderChatState();
  }
}

async function acceptChatSuggestion(id) {
  const suggestion = state.chat.suggestions.find((item) => item.id === id);
  if (!suggestion || suggestion.status === "candidate_pending") return;
  try {
    const result = await apiJson(`/api/chat/suggestions/${encodeURIComponent(id)}/accept`, {
      method: "POST",
      body: "{}",
    });
    suggestion.status = "candidate_pending";
    suggestion.candidate_id = result.candidate.id;
    if (result.candidate) state.candidates.unshift(result.candidate);
    state.selectedId = result.candidate.id;
    state.adminNotice = `相談から ${result.candidate.id} を確認待ちへ追加しました`;
    renderAll();
  } catch (error) {
    state.adminNotice = `相談候補の追加に失敗しました: ${error.message}`;
    renderAll();
  }
}

function openChatDrawer() {
  const drawer = byId("chatDrawer");
  const backdrop = byId("chatDrawerBackdrop");
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
  document.body.classList.add("chat-open");
  byId("chatDrawerInput")?.focus();
}

function closeChatDrawer() {
  const drawer = byId("chatDrawer");
  const backdrop = byId("chatDrawerBackdrop");
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  document.body.classList.remove("chat-open");
}

function label(value) {
  const labels = {
    all: "すべて",
    pending: "確認待ち",
    edited: "編集済み",
    approved: "GO済み",
    rejected: "不要",
    archived: "アーカイブ",
    web: "Web手入力",
    slack: "Slack",
    misskey: "Misskey",
    knowledge_vault: "knowledge-vault",
    chat: "AI相談",
    idea: "アイデア",
    consideration: "検討",
    concern: "気になる事",
    todo: "TODO",
    schedule_candidate: "予定候補",
    has_missing: "不足あり",
    complete: "不足なし",
    high: "高",
    medium: "中",
    low: "低",
  };
  return labels[value] || String(value).replaceAll("_", " ");
}

function selectedCandidate() {
  return state.candidates.find((candidate) => candidate.id === state.selectedId) || state.candidates[0] || null;
}

function displayCandidateTitle(candidate) {
  return candidate?.todo?.trim() || candidate?.title || "候補名なし";
}

function executionLink(candidateId) {
  return state.executionLinks.find((link) => link.candidate_id === candidateId) || null;
}

function executionTaskState(candidateId) {
  return state.executionTaskStates.find((item) => item.candidate_id === candidateId) || null;
}

function filteredCandidates() {
  const status = byId("filterStatus")?.value || "all";
  const source = byId("filterSource")?.value || "all";
  const kind = byId("filterKind")?.value || "all";
  const missing = byId("filterMissing")?.value || "all";

  return state.candidates.filter((candidate) => {
    const statusOk = status === "all" || candidate.status === status;
    const sourceOk = source === "all" || candidate.source === source;
    const kindOk = kind === "all" || candidate.kind === kind;
    const missingOk =
      missing === "all" ||
      (missing === "has_missing" && candidate.missing.length > 0) ||
      (missing === "complete" && candidate.missing.length === 0);
    return statusOk && sourceOk && kindOk && missingOk;
  });
}

function renderFilters() {
  [
    ["filterStatus", options.status],
    ["filterSource", options.source],
    ["filterKind", options.kind],
    ["filterMissing", options.missing],
  ].forEach(([id, values]) => {
    const select = byId(id);
    select.innerHTML = values.map((value) => `<option value="${value}">${label(value)}</option>`).join("");
    select.addEventListener("change", renderAll);
  });
}

function renderSourceMix() {
  const counts = state.candidates.reduce((acc, candidate) => {
    acc[candidate.source] = (acc[candidate.source] || 0) + 1;
    return acc;
  }, {});
  const max = Math.max(...sourceSettings.map((source) => counts[source.id] || 0), 1);
  byId("sourceMix").innerHTML = sourceSettings
    .map(
      (source) => {
        const count = counts[source.id] || 0;
        return `
        <div class="source-item ${source.enabled ? "" : "source-item-disabled"}">
          <strong>${source.name}</strong>
          <span class="muted">${count}件 / ${source.enabled ? "有効" : "停止中"}</span>
          <div class="source-bar"><span style="width: ${(count / max) * 100}%"></span></div>
        </div>
      `;
      },
    )
    .join("");
}

function renderKindMix() {
  const counts = state.candidates.reduce((acc, candidate) => {
    acc[candidate.kind] = (acc[candidate.kind] || 0) + 1;
    return acc;
  }, {});
  const max = Math.max(...kindDisplayOrder.map((kind) => counts[kind] || 0), 1);
  byId("kindMix").innerHTML = kindDisplayOrder
    .map(
      (kind) => {
        const count = counts[kind] || 0;
        return `
        <div class="source-item">
          <strong>${label(kind)}</strong>
          <span class="muted">${count}件</span>
          <div class="source-bar"><span style="width: ${(count / max) * 100}%"></span></div>
        </div>
      `;
      },
    )
    .join("");
}

function renderFlowHealth() {
  const total = state.candidates.length;
  const pending = state.candidates.filter((item) => item.status === "pending").length;
  const missing = state.candidates.filter((item) => item.missing.length > 0).length;
  const scheduledMinutes = state.candidates.reduce((sum, item) => {
    const match = item.schedule.match(/(\d+)\s*min/);
    return sum + (match ? Number.parseInt(match[1], 10) : 0);
  }, 0);
  const highConfidencePending = state.candidates.filter(
    (item) => item.status === "pending" && item.confidence === "high",
  ).length;
  const stats = [
    ["タスク候補総数", `${total}件`],
    ["未処理の比率", `${Math.round((pending / Math.max(total, 1)) * 100)}%`],
    ["不足項目あり", `${missing}件`],
    ["予定化の分量", `${scheduledMinutes}分`],
    ["用意済待機タスク", `${highConfidencePending}件`],
  ];
  byId("flowHealth").innerHTML = stats
    .map(
      ([title, value]) => `
        <div class="health-item">
          <strong>${value}</strong>
          <span>${title}</span>
        </div>
      `,
    )
    .join("");
}

function renderAttentionItems() {
  const attention = state.candidates
    .filter((item) => item.missing.length > 0 || item.confidence === "low" || item.source === "knowledge_vault")
    .slice(0, 5);
  byId("attentionItems").innerHTML = attention
    .map(
      (item) => `
        <div class="decision-item">
          <strong>${displayCandidateTitle(item)}</strong>
          <p>${label(item.source)} / ${item.missing.length ? `missing: ${item.missing.join(", ")}` : "context check"}</p>
        </div>
      `,
    )
    .join("");
}

function renderDecisionLog() {
  const log = state.log.slice(0, 5);
  byId("decisionLog").innerHTML =
    log.length === 0
      ? '<div class="decision-item"><strong>まだ判断なし</strong><p>確認待ちキューの GO / 編集 / 不要 / アーカイブで判断ログが増えます。</p></div>'
      : log
          .map(
            (item) => `
            <div class="decision-item">
              <strong>${item.action}: ${item.title}</strong>
              <p>${item.time}${item.operationId ? ` / 操作ID: ${item.operationId}` : ""}</p>
            </div>
          `,
          )
           .join("");
}

function createOperationId(action) {
  const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  return `ui-${action}-${suffix}`.slice(0, 96);
}

function decisionEvidence(result, fallbackOperationId) {
  const operationId = result?.decision?.operationId || result?.operation_id || fallbackOperationId;
  const http = result?.__httpStatus ? `HTTP ${result.__httpStatus} / ` : "";
  return `${http}操作ID: ${operationId || "未取得"}`;
}

function setVikunjaLink(id, href) {
  const link = byId(id);
  if (!link) return;
  if (href) {
    link.href = href;
    link.classList.remove("is-disabled");
    link.removeAttribute("aria-disabled");
    link.removeAttribute("tabindex");
  } else {
    link.href = "#tasks";
    link.classList.add("is-disabled");
    link.setAttribute("aria-disabled", "true");
    link.setAttribute("tabindex", "-1");
  }
}

function renderVikunjaOverview() {
  const overview = state.vikunjaOverview;
  const project = overview.project;
  const taskList = byId("vikunjaRecentTasks");
  const summary = byId("vikunjaSummary");
  const status = byId("vikunjaOverviewStatus");
  if (!taskList || !summary || !status) return;

  setVikunjaLink("tasksOpenLink", project?.url);
  setVikunjaLink("ganttExternalLink", project?.url);
  if (overview.reason === "loading") {
    status.textContent = "Vikunja読込中";
    summary.innerHTML = '<span class="muted">Tasks側の概要を取得しています。</span>';
    taskList.innerHTML = '<div class="task-overview-empty">直近タスクを読込中</div>';
    return;
  }
  if (!overview.available) {
    status.textContent = overview.reason === "not-configured" ? "未接続" : "接続エラー";
    const nextAction = overview.reason === "not-configured"
      ? "Vikunjaは未接続です。設定後に更新してください。"
      : "Vikunjaへ接続できません。更新して再試行してください。";
    summary.innerHTML = `<span class="muted">${nextAction}</span>`;
    taskList.innerHTML = `<div class="task-overview-empty">${nextAction}</div>`;
    return;
  }
  status.textContent = project?.title || "Tasks側";
  summary.innerHTML = [
    ["全タスク", `${overview.summary.total}件`],
    ["未完了", `${overview.summary.open}件`],
    ["完了", `${overview.summary.done}件`],
  ]
    .map(([title, value]) => `<div class="task-overview-metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(title)}</span></div>`)
    .join("");
  taskList.innerHTML = overview.tasks.length
    ? overview.tasks
        .map(
          (task) => `
          <div class="task-overview-row">
            <div class="task-overview-title">
              ${task.url ? `<a href="${escapeHtml(task.url)}" target="_blank" rel="noreferrer">${escapeHtml(task.title)}</a>` : `<strong>${escapeHtml(task.title)}</strong>`}
              <span class="muted">#${escapeHtml(task.id)} / ${task.done ? "完了" : `${escapeHtml(task.percentDone)}%`}</span>
            </div>
            <span class="task-overview-meta">期限 ${escapeHtml(formatVikunjaDate(task.dueDate))}</span>
          </div>
        `,
        )
        .join("")
    : '<div class="task-overview-empty">Tasks側にタスクはありません。</div>';
}

async function refreshVikunjaOverview() {
  state.vikunjaOverview = { ...state.vikunjaOverview, available: false, reason: "loading", project: null, tasks: [] };
  renderVikunjaOverview();
  try {
    state.vikunjaOverview = await apiJson("/api/integrations/vikunja/overview");
  } catch (error) {
    console.warn(error);
    state.vikunjaOverview = { available: false, reason: "unavailable", project: null, tasks: [], summary: { total: 0, open: 0, done: 0 } };
  }
  renderVikunjaOverview();
}

function renderQueue() {
  const rows = filteredCandidates();
  byId("queueTable").innerHTML = rows
    .map(
      (candidate) => `
      <tr data-id="${candidate.id}" class="${candidate.id === state.selectedId ? "selected" : ""}">
        <td><span class="badge ${candidate.status}">${label(candidate.status)}</span></td>
        <td><strong>${escapeHtml(displayCandidateTitle(candidate))}</strong><div class="muted">${candidate.id}</div></td>
        <td>${label(candidate.kind)}</td>
        <td>${label(candidate.source)}<div class="muted">${candidate.sourceLabel}</div></td>
        <td><div class="tag-list">${candidate.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div></td>
        <td>${label(candidate.confidence)}</td>
        <td>${candidate.missing.length ? candidate.missing.join(", ") : "なし"}</td>
        <td>${candidate.occurred}</td>
      </tr>
    `,
    )
    .join("");

  document.querySelectorAll("#queueTable tr").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedId = row.dataset.id;
      renderAll();
    });
  });
}

function renderDetail() {
  const candidate = selectedCandidate();
  if (!candidate) {
    byId("detailPane").innerHTML = '<div class="detail-empty">候補を選択すると、SQLite に保存された詳細を表示します。</div>';
    return;
  }
  if (state.editingId === candidate.id) {
    byId("detailPane").innerHTML = `
      <div class="panel-header">
        <h3>${escapeHtml(displayCandidateTitle(candidate))}</h3>
        <span class="badge ${candidate.status}">${label(candidate.status)}</span>
      </div>
      <form class="detail-edit-form" id="detailEditForm">
        <label>
          <span>タイトル</span>
          <input name="title" type="text" value="${candidate.title}" />
        </label>
        <label>
          <span>AI要約</span>
          <textarea name="summary" rows="3">${candidate.summary}</textarea>
        </label>
        <label>
          <span>抜粋</span>
          <textarea name="excerpt" rows="4">${candidate.excerpt}</textarea>
        </label>
        <label>
          <span>TODO案</span>
          <input name="todo" type="text" value="${candidate.todo}" />
        </label>
        <label>
          <span>予定案</span>
          <input name="schedule" type="text" value="${candidate.schedule}" />
        </label>
        <label>
          <span>タグ</span>
          <input name="tags" type="text" value="${candidate.tags.join(", ")}" />
        </label>
        <div class="actions edit-actions">
          <button class="secondary-button" type="submit" data-save-mode="edited">保存</button>
          <button class="primary-button" type="submit" data-save-mode="approved">保存してGO</button>
          <button class="ghost-button" type="button" data-cancel-edit>戻る</button>
        </div>
      </form>
    `;
    byId("detailEditForm").addEventListener("submit", saveCandidateEdit);
    byId("detailPane").querySelector("[data-cancel-edit]").addEventListener("click", () => {
      state.editingId = "";
      renderDetail();
    });
    return;
  }
  const link = executionLink(candidate.id);
  const taskState = executionTaskState(candidate.id);
  byId("detailPane").innerHTML = `
    <div class="panel-header">
      <h3>${escapeHtml(displayCandidateTitle(candidate))}</h3>
      <span class="badge ${candidate.status}">${label(candidate.status)}</span>
    </div>
    <div class="detail-block">
      <span class="detail-label">AI要約</span>
      <p>${candidate.summary}</p>
    </div>
    <div class="detail-block">
      <span class="detail-label">抜粋</span>
      <p>${candidate.excerpt}</p>
    </div>
    <div class="detail-block">
      <span class="detail-label">TODO案</span>
      <p>${candidate.todo}</p>
    </div>
    <div class="detail-block">
      <span class="detail-label">予定案</span>
      <p>${candidate.schedule}</p>
    </div>
    <div class="detail-block">
      <span class="detail-label">参照元</span>
      <p>${candidate.sourcePath}</p>
    </div>
    <div class="detail-block">
      <span class="detail-label">GO後プレビュー</span>
      <p>${candidate.preview}</p>
    </div>
    ${
      link
        ? `<div class="detail-block execution-result">
            <span class="detail-label">Tasks側の実行タスク</span>
            <p><a href="${link.external_url}" target="_blank" rel="noreferrer">Tasks側で開く</a> <span class="muted">#${link.external_task_id} / ${link.sync_state}</span></p>
            <p class="muted">状態mirror: ${taskState ? `${taskState.done ? "完了" : "未完了"} / ${escapeHtml(String(taskState.percent_done ?? 0))}% / 期限 ${escapeHtml(formatVikunjaDate(taskState.due_date))}` : "再取得待ち"}</p>
            <p class="muted">期限・担当・進捗・完了はTasks側で編集します。</p>
          </div>`
        : ""
    }
    <div class="actions">
      <button class="primary-button" type="button" data-action="approved">GO</button>
      <button class="secondary-button" type="button" data-edit-candidate>編集</button>
      <button class="danger-button" type="button" data-action="rejected">不要</button>
      <button class="ghost-button" type="button" data-action="archived">アーカイブ</button>
    </div>
  `;
  document.querySelectorAll("#detailPane [data-action]").forEach((button) => {
    button.addEventListener("click", () => updateCandidateStatus(candidate.id, button.dataset.action));
  });
  byId("detailPane").querySelector("[data-edit-candidate]").addEventListener("click", () => {
    state.editingId = candidate.id;
    renderDetail();
  });
}

async function saveCandidateEdit(event) {
  event.preventDefault();
  const submitter = event.submitter;
  const candidate = selectedCandidate();
  const form = new FormData(event.currentTarget);
  const payload = {
    title: form.get("title").toString().trim(),
    summary: form.get("summary").toString().trim(),
    excerpt: form.get("excerpt").toString().trim(),
    todo: form.get("todo").toString().trim(),
    schedule: form.get("schedule").toString().trim(),
    tags: form.get("tags").toString(),
    status: submitter?.dataset.saveMode || "edited",
    operation_id: createOperationId(submitter?.dataset.saveMode || "edited"),
  };
  if (payload.status === "approved" && !confirmCandidateAction("approved")) return;
  try {
    const updated = await apiJson(`/api/candidates/${encodeURIComponent(candidate.id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    const execution = payload.status === "approved" ? await executeCandidate(updated.id, payload.operation_id) : null;
    state.editingId = "";
    const evidence = decisionEvidence(execution || updated, payload.operation_id);
    await refreshBootstrap(`${payload.status === "approved" ? "保存してGOしました" : "候補を保存しました"}（${evidence}）`);
    return;
  } catch (error) {
    state.adminNotice = `候補の保存に失敗しました: ${error.message}`;
  }
  state.editingId = "";
  renderAll();
}

async function executeCandidate(id, operationId = createOperationId("approved")) {
  const link = await apiJson(`/api/candidates/${encodeURIComponent(id)}/execution`, {
    method: "POST",
    body: JSON.stringify({ operation_id: operationId }),
  });
  const index = state.executionLinks.findIndex((item) => item.candidate_id === id);
  if (index >= 0) state.executionLinks[index] = link;
  else state.executionLinks.push(link);
  const candidate = state.candidates.find((item) => item.id === id);
  if (candidate) candidate.status = "approved";
  state.adminNotice = `Vikunja task #${link.external_task_id} を作成しました（${decisionEvidence(link, operationId)}）`;
  void refreshVikunjaOverview();
  return link;
}

function confirmCandidateAction(status) {
  const actionLabels = { approved: "GO", rejected: "不要", archived: "アーカイブ" };
  const action = actionLabels[status] || status;
  if (typeof window === "undefined" || typeof window.confirm !== "function") return true;
  return window.confirm(`「${action}」を実行します。Hubの実データと判断ログを変更します。続けますか？`);
}

async function updateCandidateStatus(id, status) {
  const candidate = state.candidates.find((item) => item.id === id);
  if (!candidate) return;
  if (!confirmCandidateAction(status)) return;
  try {
    const operationId = createOperationId(status);
    let result;
    if (status === "approved") {
      result = await executeCandidate(id, operationId);
    } else {
      result = await apiJson(`/api/candidates/${encodeURIComponent(id)}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status, operation_id: operationId }),
      });
    }
  } catch (error) {
    state.adminNotice = `状態変更に失敗しました: ${error.message}`;
    renderAll();
    return;
  }
  await refreshBootstrap(`${label(status)}として判断を保存しました（${decisionEvidence(result, operationId)}）`);
}

function renderObjectPreview() {
  const linked = state.executionLinks
    .map((link) => ({ link, candidate: state.candidates.find((item) => item.id === link.candidate_id) }))
    .filter((item) => item.candidate);
  byId("objectPreview").innerHTML =
    linked.length === 0
      ? '<div class="source-item"><strong>Tasks側の登録なし</strong><span class="muted">HubでGOするとTasks側へ登録されます。</span></div>'
      : linked
          .map(
            ({ link, candidate }) => `
          <div class="source-item">
            <strong>${escapeHtml(displayCandidateTitle(candidate))}</strong>
            <span class="muted"><a href="${link.external_url}" target="_blank" rel="noreferrer">Tasks側タスク #${link.external_task_id}</a> / ${link.sync_state}</span>
          </div>
        `,
          )
          .join("");
}

function renderWorker() {
  const active = state.candidates.filter((item) => item.status !== "rejected" && item.status !== "archived").slice(0, 4);
  byId("todayTasks").innerHTML = active
    .map(
      (item) => `
        <div class="task-item">
          <strong>${item.todo}</strong>
          <p>${item.schedule}</p>
          <div class="tag-list">${item.tags.slice(0, 3).map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
        </div>
      `,
    )
    .join("");
  const selected = selectedCandidate();
  byId("codexPrompt").textContent = [
    "P0 task start",
    `Target: ${selected?.todo || "確認待ち候補を選択"}`,
    `Source: ${selected?.sourceLabel || "-"}`,
    `Context: ${selected?.summary || "候補がまだありません"}`,
    "Rules: read AGENTS.md, PROJECT.md, tech-stack.md, docs/imp before edits.",
  ].join("\n");
}

function renderGantt() {
  refreshGanttScale();
  byId("weekScale").innerHTML = `
    <span></span>
    <span></span>
    <span></span>
    <div class="week-axis">
      ${weekScale
        .map(
          (week) => `
            <span class="week-tick" style="left: ${week.left}%">
              <span class="week-line"></span>
              <span class="week-label">${week.label}</span>
            </span>
          `,
        )
        .join("")}
    </div>
  `;
  const visibleTasks = ganttTasks.map(layoutGanttTask).filter(Boolean);
  if (visibleTasks.length === 0) {
    byId("ganttRows").innerHTML = '<div class="dashboard-empty gantt-empty">日付付きの候補・実行タスクはありません。予定化またはTasks側の期限を設定すると表示されます。</div>';
    return;
  }
  byId("ganttRows").innerHTML = visibleTasks
    .map(
      (task) => `
        <div class="gantt-row">
          <div><strong>${escapeHtml(task.title)}</strong><div class="muted">${escapeHtml(task.startDate)}${task.endDate !== task.startDate ? ` - ${escapeHtml(task.endDate)}` : ""} / 依存: ${escapeHtml(task.dependency)}</div></div>
          <div>${escapeHtml(task.owner)}</div>
          <div>${escapeHtml(task.progress)}%</div>
          <div class="timeline" aria-label="${escapeHtml(task.title)} timeline">
            ${weekScale.map((week) => `<span class="timeline-gridline" style="left: ${week.left}%"></span>`).join("")}
            <span class="timeline-bar ${task.state}" style="left: ${task.start}%; width: ${task.span}%"></span>
          </div>
        </div>
      `,
    )
    .join("");
}

function scheduleGanttLayout() {
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      renderGantt();
    });
  });
}

function renderTags() {
  byId("tagMaster").innerHTML = tagMaster
    .map(
      (tag) => `
        <button class="tag tag-toggle ${tag.visible ? "" : "tag-hidden"}" type="button" data-tag-id="${tag.id}" data-tag-visible="${tag.visible ? "1" : "0"}">
          ${tag.name}
        </button>
      `,
    )
    .join("");
  document.querySelectorAll("[data-tag-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await apiJson(`/api/admin/tags/${button.dataset.tagId}`, {
          method: "PATCH",
          body: JSON.stringify({ visible: button.dataset.tagVisible !== "1" }),
        });
        await refreshBootstrap("タグ表示を保存しました");
      } catch (error) {
        state.adminNotice = `タグの保存に失敗しました: ${error.message}`;
        renderAll();
      }
    });
  });
}

function renderAdminControls(targetId, items, group = "") {
  byId(targetId).innerHTML = items
    .map(
      (item) => `
        <div class="admin-control ${item.enabled ? "enabled" : "disabled"}">
          <div>
            <div class="admin-control-heading">
              <strong>${item.name}</strong>
              ${item.controlType ? `<span class="control-state ${item.enabled ? "control-state--enabled" : "control-state--disabled"}">${item.enabled ? "有効" : "停止中"}</span>` : ""}
            </div>
            <p>${item.detail}</p>
            <span class="muted">${item.meta}</span>
          </div>
          <div class="admin-buttons">
            ${item.action ? `<button class="primary-button" type="button" data-admin-action="${item.action}">取込</button>` : ""}
            ${item.controlType ? `<button class="${item.enabled ? "ghost-button" : "secondary-button"}" type="button" ${item.locked ? "disabled" : ""} data-admin-toggle="${item.controlType}" data-admin-id="${item.id}" data-admin-enabled="${item.enabled ? "1" : "0"}" ${group ? `data-admin-group="${group}"` : ""}>${item.enabled ? "無効化" : "有効化"}</button>` : ""}
          </div>
        </div>
      `,
    )
    .join("");
}

function observabilitySourceLabel(source) {
  return {
    knowledge_vault: "knowledge-vault",
    slack: "Slack",
    vikunja_reconcile: "Vikunja reconcile",
  }[source] || source;
}

function renderObservability() {
  const status = byId("observabilityStatus");
  const metricsTarget = byId("observabilityMetrics");
  const target = byId("observabilityRuns");
  if (!status || !metricsTarget || !target) return;
  const observability = state.observability;
  if (!observability) {
    status.textContent = "観測結果を読み込み中";
    metricsTarget.innerHTML = "";
    target.innerHTML = "";
    return;
  }
  const runs = Object.values(observability.latestBySource || {});
  const backups = observability.latestBackups || [];
  status.textContent = runs.length || backups.length
    ? `source ${runs.length}系統 / backup ${backups.length}世代を確認可能`
    : "まだ同期・backupの実行記録はありません";
  const operations = observability.operations || {};
  const candidateCounts = operations.candidateCounts || {};
  const executionCounts = operations.executionCounts || {};
  const metricItems = [
    ["候補", candidateCounts.total || 0],
    ["確認待ち", candidateCounts.pending || 0],
    ["GO", operations.decisionCounts?.approved || 0],
    ["Tasks完了", executionCounts.completed || 0],
    ["不足あり", operations.missingCandidates || 0],
  ];
  metricsTarget.innerHTML = metricItems.map(([label, value]) => `
    <div class="observability-metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>
  `).join("");
  const runItems = runs
    .sort((left, right) => String(left.source).localeCompare(String(right.source)))
    .map((run) => `
      <div class="observability-item">
        <strong>${escapeHtml(observabilitySourceLabel(run.source))}</strong>
        <span class="observability-state observability-state--${escapeHtml(run.state)}">${escapeHtml(run.state)}</span>
        <span class="muted">${run.created}件作成 / ${run.skipped}件skip / ${run.failed}件失敗</span>
        <small>${escapeHtml(run.finished_at || run.started_at || "実行中")}</small>
      </div>
    `);
  const backupItems = backups.slice(0, 3).map((backup) => `
    <div class="observability-item observability-item--backup">
      <strong>Hub backup</strong>
      <span class="observability-state observability-state--${escapeHtml(backup.integrity || "unavailable")}">${escapeHtml(backup.integrity || "unavailable")}</span>
      <span class="muted">${Number(backup.sizeBytes || 0).toLocaleString()} bytes / SHA-256 ${escapeHtml(String(backup.sha256 || "").slice(0, 12))}…</span>
      <small>${escapeHtml(backup.createdAt || backup.name || "")}</small>
    </div>
  `);
  target.innerHTML = [...runItems, ...backupItems].join("") || '<div class="observability-empty">記録が増えるとここに表示されます。</div>';
}

async function refreshObservability(notice = "") {
  try {
    state.observability = await apiJson("/api/observability");
    if (notice) state.adminNotice = notice;
  } catch (error) {
    state.adminNotice = `運用観測の取得に失敗しました: ${error.message}`;
  }
  renderAll();
}

function bindAdminActions() {
  document.querySelectorAll("[data-admin-action='importKnowledgeVault']").forEach((button) => {
    button.addEventListener("click", async () => {
      button.textContent = "取り込み中";
      button.disabled = true;
      try {
        await apiJson("/api/import/knowledge-vault", {
          method: "POST",
          body: JSON.stringify({ limit: 20 }),
        }).then((result) => {
          state.adminNotice = `knowledge-vault: imported ${result.imported} / skipped ${result.skipped} / scanned ${result.scanned}`;
        });
        const bootstrap = await apiJson("/api/bootstrap");
        state.candidates = bootstrap.candidates;
        state.log = bootstrap.log || state.log;
        renderAll();
      } catch (error) {
        console.warn(error);
        button.textContent = "失敗";
      }
    });
  });
  document.querySelectorAll("[data-admin-toggle]").forEach((button) => {
    button.addEventListener("click", async () => {
      const type = button.dataset.adminToggle;
      const id = button.dataset.adminId;
      const nextEnabled = button.dataset.adminEnabled !== "1";
      const group = button.dataset.adminGroup;
      const endpoint =
        type === "source"
          ? `/api/admin/sources/${encodeURIComponent(id)}`
          : type === "prompt"
            ? `/api/admin/prompt-templates/${encodeURIComponent(id)}`
            : `/api/admin/settings/${encodeURIComponent(group)}/${encodeURIComponent(id)}`;
      button.disabled = true;
      try {
        await apiJson(endpoint, {
          method: "PATCH",
          body: JSON.stringify({ enabled: nextEnabled }),
        });
        await refreshBootstrap("設定を保存しました");
      } catch (error) {
        console.warn(error);
        button.disabled = false;
      }
    });
  });
}

function applyBootstrap(bootstrap) {
  state.candidates = bootstrap.candidates;
  state.selectedId = bootstrap.candidates.some((candidate) => candidate.id === state.selectedId)
    ? state.selectedId
    : bootstrap.candidates[0]?.id || "";
  state.log = bootstrap.log || [];
  state.executionLinks = bootstrap.executionLinks || [];
  state.executionTaskStates = bootstrap.executionTaskStates || [];
  state.dbPath = bootstrap.dbPath || "";
  ganttTasks = bootstrap.ganttTasks || [];
  tagMaster = bootstrap.tags || [];
  if (bootstrap.sources?.length) {
    sourceSettings = bootstrap.sources.map((source) => ({
      id: source.id,
      controlType: source.id === "misskey" ? "" : "source",
      name: source.label,
      enabled: Boolean(source.enabled),
      detail: source.path,
      meta: `${source.source_kind}${source.last_imported_at ? ` / last: ${source.last_imported_at}` : ""}`,
      action: source.id === "knowledge_vault" ? "importKnowledgeVault" : "",
      locked: source.id === "misskey",
    }));
  }
  if (bootstrap.promptTemplates?.length) {
    promptSettings = bootstrap.promptTemplates.map((template) => ({
      id: template.id,
      controlType: "prompt",
      name: template.name,
      enabled: Boolean(template.enabled),
      detail: template.body,
      meta: template.target,
    }));
  }
  adminSettings.roles = (bootstrap.adminControls?.roles || []).map((item) => ({ ...item, controlType: "setting" }));
  adminSettings.automation = (bootstrap.adminControls?.automation || []).map((item) => ({ ...item, controlType: "setting" }));
  adminSettings.scopes = (bootstrap.adminControls?.scopes || []).map((item) => ({ ...item, controlType: "setting" }));
  state.adminNotice = state.adminNotice === "SQLite を読み込み中" ? "SQLite の内容を表示中" : state.adminNotice;
  byId("dashboardStatus").textContent = `SQLite / ${state.candidates.length}件`;
}

async function refreshBootstrap(notice = "") {
  const bootstrap = await apiJson("/api/bootstrap");
  applyBootstrap(bootstrap);
  try {
    state.observability = await apiJson("/api/observability");
  } catch (error) {
    console.warn(error);
    if (!state.observability) state.observability = { latestBySource: {}, latestBackups: [], operations: {} };
  }
  if (notice) state.adminNotice = notice;
  renderAll();
}

async function addManualCandidate(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const title = form.get("title").toString().trim() || "Untitled intake";
  const body = form.get("body").toString().trim();
  const tags = form
    .get("tags")
    .toString()
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
  const payload = {
    title,
    kind: form.get("kind").toString(),
    url: form.get("url").toString() || "web://manual",
    tags: tags.length ? tags : ["manual"],
    body,
    schedule: form.get("schedule").toString(),
  };
  let candidate;
  try {
    candidate = await apiJson("/api/candidates", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch (error) {
    state.adminNotice = `書き入れの保存に失敗しました: ${error.message}`;
    renderAll();
    return;
  }
  state.candidates.unshift(candidate);
  state.selectedId = candidate.id;
  state.log.push({ action: "created", title, time: new Date().toLocaleString("ja-JP") });
  renderAll();
  document.location.hash = "queue";
  closeIntakeDrawer();
}

async function copyPrompt(event) {
  const button = event.currentTarget;
  const original = "コピー";
  try {
    const text = byId("codexPrompt").textContent;
    if (!navigator.clipboard?.writeText) throw new Error("clipboard API が利用できません");
    await navigator.clipboard.writeText(text);
    button.textContent = "コピーしました";
  } catch (error) {
    button.textContent = "コピー失敗";
    state.adminNotice = `コピーに失敗しました: ${error.message}`;
    renderAll();
  }
  window.setTimeout(() => {
    button.textContent = original;
  }, 1200);
}

async function createTag(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const name = form.get("name").toString().trim();
  if (!name) return;
  try {
    await apiJson("/api/admin/tags", { method: "POST", body: JSON.stringify({ name }) });
    event.currentTarget.reset();
    await refreshBootstrap("タグを追加しました");
  } catch (error) {
    state.adminNotice = `タグ追加に失敗しました: ${error.message}`;
    renderAll();
  }
}

async function importSlackPayload(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const rawMessages = form.get("messages").toString().trim();
  let messages;
  try {
    messages = JSON.parse(rawMessages);
    if (!Array.isArray(messages)) throw new Error("配列形式で入力してください");
  } catch (error) {
    state.adminNotice = `Slack payload を読み取れません: ${error.message}`;
    renderAll();
    return;
  }
  try {
    const result = await apiJson("/api/import/slack", {
      method: "POST",
      body: JSON.stringify({
        channelName: "memo-ideas",
        channelUrl: "https://unibell4-dev.slack.com/archives/C0BG4TCPAUD",
        messages,
      }),
    });
    event.currentTarget.reset();
    await refreshBootstrap(`Slack memo-ideas: imported ${result.imported} / skipped ${result.skipped} / scanned ${result.scanned}`);
  } catch (error) {
    state.adminNotice = `Slack 取り込みに失敗しました: ${error.message}`;
    renderAll();
  }
}

function renderAll() {
  renderFlowHealth();
  renderSourceMix();
  renderKindMix();
  renderVikunjaOverview();
  renderAttentionItems();
  renderDecisionLog();
  renderQueue();
  renderDetail();
  renderObjectPreview();
  renderWorker();
  renderGantt();
  scheduleGanttLayout();
  renderTags();
  renderObservability();
  renderAdminControls("sourceSettings", sourceSettings);
  renderAdminControls("roleSettings", adminSettings.roles, "roles");
  renderAdminControls("automationSettings", adminSettings.automation, "automation");
  renderAdminControls("promptSettings", promptSettings);
  renderAdminControls("scopeSettings", adminSettings.scopes, "scopes");
  renderChatState();
  byId("adminStatus").textContent = state.adminNotice;
  bindAdminActions();
}

function bindStaticActions() {
  document.querySelectorAll("[data-scroll-target]").forEach((button) => {
    button.addEventListener("click", () => {
      scrollToSection(byId(button.dataset.scrollTarget), "smooth");
    });
  });
  document.querySelectorAll("[data-open-intake]").forEach((button) => {
    button.addEventListener("click", openIntakeDrawer);
  });
  document.querySelectorAll("[data-close-intake]").forEach((button) => {
    button.addEventListener("click", closeIntakeDrawer);
  });
  byId("drawerBackdrop").addEventListener("click", closeIntakeDrawer);
  document.querySelectorAll("[data-open-chat]").forEach((button) => {
    button.addEventListener("click", openChatDrawer);
  });
  document.querySelectorAll("[data-close-chat]").forEach((button) => {
    button.addEventListener("click", closeChatDrawer);
  });
  byId("chatDrawerBackdrop").addEventListener("click", closeChatDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeIntakeDrawer();
      closeChatDrawer();
    }
  });
  byId("intakeForm").addEventListener("submit", addManualCandidate);
  byId("copyPromptButton").addEventListener("click", copyPrompt);
  byId("tagCreateForm").addEventListener("submit", createTag);
  byId("slackImportForm").addEventListener("submit", importSlackPayload);
  byId("refreshObservability").addEventListener("click", () => refreshObservability("運用観測を更新しました"));
  byId("chatPageForm").addEventListener("submit", sendChatMessage);
  byId("chatDrawerForm").addEventListener("submit", sendChatMessage);
  document.addEventListener("click", (event) => {
    const promptButton = event.target.closest("[data-chat-prompt]");
    if (!promptButton) return;
    const input = byId(document.body.classList.contains("chat-page") ? "chatPageInput" : "chatDrawerInput");
    if (!input) return;
    input.value = promptButton.dataset.chatPrompt || "";
    input.focus();
  });
  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-refresh-vikunja]")) refreshVikunjaOverview();
    const acceptButton = event.target.closest("[data-accept-chat-suggestion]");
    if (acceptButton) acceptChatSuggestion(acceptButton.dataset.acceptChatSuggestion);
  });
}

function scrollToSection(target, behavior) {
  if (!target) return;
  target.scrollIntoView({ behavior, block: "start" });
}

function openIntakeDrawer() {
  const drawer = byId("intakeDrawer");
  const backdrop = byId("drawerBackdrop");
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  backdrop.hidden = false;
  document.body.classList.add("drawer-open");
}

function closeIntakeDrawer() {
  const drawer = byId("intakeDrawer");
  const backdrop = byId("drawerBackdrop");
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
  backdrop.hidden = true;
  document.body.classList.remove("drawer-open");
}

function applyHashState() {
  const hash = document.location.hash.replace("#", "");
  if (hash === "intake") {
    openIntakeDrawer();
    return;
  }
  if (hash) {
    const scrollToHash = () => {
      const target = byId(hash);
      if (!target) return;
      scrollToSection(target, "auto");
    };
    window.requestAnimationFrame(scrollToHash);
    window.setTimeout(scrollToHash, 120);
    window.setTimeout(scrollToHash, 420);
  }
}

renderFilters();
bindStaticActions();

async function initApp() {
  try {
    const [bootstrap, observability] = await Promise.all([
      apiJson("/api/bootstrap"),
      apiJson("/api/observability"),
    ]);
    applyBootstrap(bootstrap);
    state.observability = observability;
  } catch (error) {
    console.warn(error);
  }
  renderAll();
  applyHashState();
  refreshVikunjaOverview();
  refreshChatBootstrap();
}

initApp();
window.addEventListener("hashchange", applyHashState);
window.addEventListener("visibilitychange", () => {
  if (!document.hidden) scheduleGanttLayout();
});
window.addEventListener("resize", scheduleGanttLayout);
