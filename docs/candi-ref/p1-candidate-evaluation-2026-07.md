# P1候補評価 2026-07

## 評価の起点

P0実DBは候補19件、判断0件、execution link 0件である。契約E2Eは成立しているが日常運用データがないため、P1では「常設して使い、観測できること」を大型基盤移行より優先する。

## 評価結果

| 候補 | 判定 | P1で行うこと | 導入ゲート |
| --- | --- | --- | --- |
| Linux定期入口worker | 採用・最優先 | knowledge-vaultから開始し、source別run / cursor / errorを記録 | 手動importと同じ冪等結果になる |
| 運用監視・backup | 採用・最優先 | health、同期結果、backup検証、reconcile結果を可視化 | 常設運用開始前 |
| Vikunja fork配信 | 採用・最優先 | `325bc5475` を別tagでbuild、blue/green、rollback、upstream追随手順 | stable imageへ即時復帰可能 |
| Slack実運用 | 採用 | 最初の実投稿をconnector payloadで取り込み、cursor / dedupeを検証 | 認証情報をHubに持たせない |
| Misskey実接続 | PoC採用 | REST差分取得・Streaming・実験的Webhookを比較 | 最小read権限、秘密分離、重複0 |
| 重複束ね | PoC採用 | 自動統合せず類似候補を提案表示 | 誤束ねを取消可能 |
| 部分自動確定 | 保留付きPoC | decision実績を集計し、対象segmentだけdry-run | 十分な判断件数と誤確定0の証拠 |
| Google Calendar | 後半PoC | ユーザー操作による一方向event作成、idempotency | TODOと予定の所有権確定後 |
| PostgreSQL | 条件付き保留 | schema / migration dry-runだけ準備 | 複数writer、認証、競合、規模のいずれか発生 |
| Redis / BullMQ | 保留 | systemd oneshotで不足が観測された時だけ再評価 | 並列queue・高度なretryが必要 |
| Better Auth / 権限 | 設計のみ | resource / action matrixと移行境界を決める | 二人目・外部協力者を招く前 |
| Next.js等への全面移行 | 保留 | P1機能と同時に移行しない | auth / team UIや保守限界が顕在化 |

## 判断理由

### Misskey

公式Streaming APIはWebSocket channel方式で、複数channelを1接続で購読できる。Webhookはsecret headerを持つ一方、公式にもexperimentalでpayload仕様が不安定と明記される。P1の初手は、取得漏れを再照合できる差分pollingを基準にし、Streamingは低遅延補助、Webhookは採用前PoCとする。

### Calendar

Google Calendarのincremental syncは初回full sync後にsync tokenを保存し、token無効時の410ではfull syncへ戻す設計が必要である。P1では双方向同期を始めず、まずユーザーGOによる一方向作成と外部event idの冪等保存だけをPoCする。

### PostgreSQL

PostgreSQL 18はJSONBとGIN indexを提供するが、柔軟だから全データをJSONBへ寄せるのではなく、状態・外部ID・時刻は通常列、可変payloadだけJSONBとする。現状19件・単一writerでは移行便益が小さい。

### 認証

Better AuthはDB-backed session、session revocation、organization / team / roleを提供する。P1では導入ではなく、Hub resourceとVikunja権限の二重管理を避けるresource-action matrixを先に作る。

### Vikunja fork

Vikunja公式はstable / unstableを分け、version切替前のbackupを必須としている。P1はstable API契約を維持し、frontend forkだけを別tagで配信する。API main追随やDB migrationと同時に切り替えない。

## 一次資料

- Vikunja versions: https://vikunja.io/docs/versions/
- Vikunja API: https://vikunja.io/docs/api-documentation/
- Vikunja backup: https://vikunja.io/docs/what-to-backup/
- Vikunja source build: https://vikunja.io/docs/build-from-sources/
- Misskey Streaming API: https://misskey-hub.net/en/docs/for-developers/api/streaming/
- Misskey Webhook: https://misskey-hub.net/en/docs/for-users/features/webhook/
- Misskey permissions: https://misskey-hub.net/en/docs/for-developers/api/permission/
- Google Calendar incremental sync: https://developers.google.com/workspace/calendar/api/guides/sync
- Google Calendar event creation: https://developers.google.com/workspace/calendar/api/guides/create-events
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- PostgreSQL text search index: https://www.postgresql.org/docs/current/textsearch-indexes.html
- Better Auth session: https://better-auth.com/docs/concepts/session-management
- Better Auth organization: https://better-auth.com/docs/plugins/organization
- Better Auth security: https://better-auth.com/docs/reference/security
