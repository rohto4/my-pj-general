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
- TODO provider navigation prepared for Vikunja
- Minimal admin settings view

Misskey, automatic AI classification, authentication, Google Calendar, and real Vikunja synchronization are not connected yet. Slack credentials are intentionally not stored in this app; Slack data enters through an explicit connector payload.
