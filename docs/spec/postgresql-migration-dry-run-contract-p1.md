# P1 PostgreSQL migration dry-run contract

P1では、現行SQLiteをすぐPostgreSQLへ置き換えない。複数writer、認証、lock競合、規模のいずれかが観測された場合に、安全に移行できるよう、移行前後で比較する値とrollback境界を先に固定する。

## 移行対象

| 区分 | SQLiteのテーブル | PostgreSQL方針 |
|---|---|---|
| 候補正本 | `candidates`, `candidate_tags`, `tags` | 状態・時刻・IDは通常列。可変の不足項目は`jsonb`へ移すが、検索対象を無制限にJSONへ寄せない |
| 判断 | `decisions` | append-only。`candidate_id`, `action`, `created_at`にindexを付ける |
| 実行連携 | `execution_links`, `execution_task_state` | 外部task IDをuniqueに保持し、Hub正本とVikunja mirrorを混ぜない |
| 同期証跡 | `sync_events`, `sync_attempts`, `source_sync_runs` | dedupe key / idempotency keyをunique制約で守る |
| 会話 | `chat_threads`, `chat_messages`, `chat_task_suggestions` | 本文はtext、provider/modelと状態を通常列で保持する |
| 設定 | `settings`, `prompt_templates` | secret本体はDBに入れず、参照名・状態だけを保存する |

## dry-run手順

1. 移行前にSQLiteの`PRAGMA integrity_check`、各対象テーブルの件数、候補ID、decisionの件数・action別集計、execution linkの外部ID、source lineageを固定する。
2. 一時PostgreSQLへschemaを作成し、同じIDを指定してデータを投入する。投入は繰り返し可能で、unique conflictを「既存一致」と「内容不一致」に分けて報告する。
3. 移行後に同じ集計とSHA-256対象列のダイジェストを取り、件数・候補ID・外部ID・source lineageが一致することを確認する。
4. `source_sync_runs`と`sync_attempts`のcursor / idempotency keyを再実行し、重複行が増えないことを確認する。
5. 一時PostgreSQLを破棄し、SQLiteは検証証跡を保存したまま正本として残す。差分がある場合は切替せず、原因を移行ログに記録する。

## rollback境界

- PostgreSQLを正本へ切り替える前は、SQLiteを読み取り可能な旧正本として保持する。
- 切替後のrollbackは、書き込み停止、PostgreSQLの移行時点バックアップ、切替前cursorの記録、Hub接続先の復元の順で行う。
- Vikunjaのtaskと`execution_links`は別のrollback対象であり、DB切替だけでtaskを再作成しない。
- いかなる差分でも候補を自動削除しない。`candidate_id`、decision、external task IDが一致しない場合は保留する。

## 現在の状態

契約と比較項目は確定したが、このWindows環境には一時PostgreSQL実行基盤がなく、実DBを使ったdry-run証跡は未取得である。P1ではSQLiteの単一writer運用を継続し、Linux常設環境または再現可能な一時PostgreSQLを用意した時点で上記手順を実行する。実行前に`docs/imp/p1-poc-readiness-2026-07-12.md`の保留判定を更新する。
