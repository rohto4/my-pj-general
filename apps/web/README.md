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

Misskey, automatic AI classification, authentication, and Google Calendar are not connected yet. Vikunja task execution is intentionally one-way after GO; the Hub reads overview data and mirrors execution state but does not duplicate the Tasks-side task editor. Slack credentials are intentionally not stored in this app; Slack data enters through an explicit connector payload.
