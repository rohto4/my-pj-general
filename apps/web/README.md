# P0 SQLite Web Demo

This is a dependency-free Node/Python demo for `pj-general` P0.

## Open

Run `server.js` through the repository start script, then open `http://127.0.0.1:4173`.

## Scope

- Manual intake form
- SQLite に保存された確認待ち候補
- Dashboard
- Worker / task summary
- SQLite persistence in `data/p0.sqlite` (gitignored)
- Real knowledge-vault file import with deduplication
- Slack connector payload import endpoint
- Real Vikunja task creation through API v1 with idempotent candidate links
- Live Vikunja project overview and recent task projection in the Hub dashboard
- Signed Vikunja webhook receiver and mirrored execution task state
- Reconciliation endpoint for missed webhook recovery
- Minimal admin settings view
- Local LLM consultation at `/chat` and a shared side drawer from the Hub
- SQLite chat history and user-confirmed task suggestions routed to the pending queue
- Read-only `get_threadline_context` tool for agent-side Hub / Tasks context lookup; task creation remains a user button action
- Operational health at `GET /api/health` with SQLite integrity and dependency states; secrets and configured URLs are not returned
- Operational observability at `GET /api/observability` with source sync runs, reconcile results, and verified backup generations; local database paths are not returned
- Consistent online SQLite backup through `backup.ps1` / `db_tool.py backup-database`
- P1 source observability through `GET /api/observability`; the oneshot adapters live in `workers/sync/`
- The same endpoint exposes candidate / decision / execution metrics without returning tokens, URLs, or database paths
- Vikunja reconcile can be run manually via the API or by the P1 `workers/reconcile` systemd timer

Misskey, automatic AI classification, authentication, and Google Calendar are not connected yet. Vikunja task execution is intentionally one-way after GO; the Hub reads overview data and mirrors execution state but does not duplicate the Tasks-side task editor. Slack credentials are intentionally not stored in this app; Slack data enters through an explicit connector payload.

## Local LLM

The default provider is Ollama at `http://127.0.0.1:11434/v1` with `gemma4:latest`. Set `LOCAL_LLM_BASE_URL`, `LOCAL_LLM_MODEL`, and optionally `LOCAL_LLM_PROVIDER` to use another OpenAI-compatible endpoint. `LOCAL_LLM_API_KEY` is server-side only. Ollama thinking is disabled by default for a visible answer; set `LOCAL_LLM_THINK=true` when needed.

## Main visual theme

The main route uses `Listening Lounge`: ink, indigo, copper, wool-gray surfaces, square structural edges, and a restrained acoustic-grid atmosphere. Its permanent theme layer is `listening-lounge.css`; it shares the existing `index.html`, `app.js`, SQLite data, and API behavior.

The former comparison route `/theme-room-03` redirects to `/`. The other temporary theme routes have been retired.

## Health and backup

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:4173/api/health
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\apps\web\backup.ps1 -BackupDir .\tmp\backup\hub
```

Health reports `ok` or `degraded`, SQLite `quick_check`, row counts, and `ok` / `not_configured` / `disabled` / `misconfigured` / `unavailable` dependency states. It does not return API tokens, secrets, configured URLs, or the source database path.

The backup command uses SQLite online backup, verifies the generated file with `quick_check`, and returns its path, size, SHA-256, integrity, and table counts as JSON. It only creates a new timestamped generation; it does not delete older backups.
