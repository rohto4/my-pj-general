# 2026-07-12 P1-A ローカルhealth・backup

## 実施

- TDDで `/api/health` の正常・未設定・無効・到達不能契約を追加した。
- DBはSQLite `quick_check`、主要table件数、file sizeを返す。
- Vikunja / local LLMは `ok` / `not_configured` / `disabled` / `misconfigured` / `unavailable` を返す。
- 応答にtoken、secret、接続URL、DB pathを含めない。
- SQLite online backupと `apps/web/backup.ps1` を追加した。
- backup生成後に別connectionでquick_checkし、SHA-256・件数をJSONで返す。
- wrapperは世代を追加するだけで、既存backupを削除しない。

## 検証

- RED: health route不在2件、backup command不在1件、wrapper不在1件を確認した。
- GREEN: Node 17 / 17、Python 3 / 3、`check.ps1`成功。
- 到達不能Vikunja / LLMは426ms以内にHTTP 200 / `degraded`。
- 実Hub health: DB `ok`、integrity `ok`、candidates 19、Vikunja `not_configured`、local LLM `ok`。
- 実backup: `tmp/backup/hub/p0-20260712-042201-020225.sqlite`。
- 147456 bytes、integrity `ok`、candidates 19、execution links 0、decisions 0。
- SHA-256: `bab37bc817f7d4112abcd6288c0262f2025b1f23ca8457d91c50406f36bb0001`。

## coverage注意

Nodeのbuilt-in coverage commandは成功したが、server / dbはchild processのためsource fileが列挙されなかった。表示された100%はcoverage証拠に使わず、integration testの契約範囲を証拠とする。

## 次

- P1開始ゲートのユーザー確認。
- Linux常設環境でbackup保持数、外部媒体複製、restore drillを行う。
- source sync / reconcile / backupの最終結果を管理画面へ集約する。
