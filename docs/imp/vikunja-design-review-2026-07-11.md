# Vikunja結合 設計レビュー 2026-07-11

## 結論

コンポーネント境界と「pj-generalを候補・判断の正本にする」方針は維持できる。
一方、Linux実装前に修正すべき設計差分が見つかったため、実機結合は以下の修正完了後に開始する。

## 発見事項

| ID | 重要度 | 発見 | 影響 | 修正方針 |
| --- | --- | --- | --- | --- |
| DR-01 | 高 | mainのAPI v2を安定版v2.3.0の契約として記載していた | 安定版ではGO登録が失敗する | stable v2.3.0は`PUT /api/v1/projects/{project}/tasks`、mainは`POST /api/v2/...`として分離する |
| DR-02 | 高 | candidate判断状態と外部同期状態を同じ遷移に並べていた | GO判断と同期失敗の意味が混ざる | candidate status、link sync state、external task stateを分離する |
| DR-03 | 高 | Webhookで受けたdone、due date、priority、assigneeの現在値の保存先が不足 | 画面表示と再照合ができない | `execution_task_state`を追加する |
| DR-04 | 中 | `sync_events.event_id`を必須にしていた | Vikunja payloadにevent IDがないreleaseで保存できない | internal ID、dedupe key、optional external event IDに分ける |
| DR-05 | 中 | API tokenとWebhook secretの保管先がVikunja側secretと混ざり得る | 権限境界が崩れる | `vikunja.env`と`pj-general.env`を分離する |
| DR-06 | 中 | 安定版image pinとAPI modeが未定義 | pull時期により契約が変わる | 初回はv2.3.0をpinし、API base pathを明示する |
| DR-07 | 中 | Docker内部Webhookはprivate addressのため標準設定で拒否され得る | Webhookが届かない | 専用networkに限定して`outgoingrequests.allownonroutableips`を有効化する |
| DR-08 | 中 | 実機受入テストが未定義 | 画面表示だけで完了扱いになる | `docs/spec/vikunja-integration-acceptance-tests-2026-07.md`を正本にする |
| DR-09 | 低 | user-tasksとapps/web READMEに旧Leantime・旧mock記述が残る | レビュー入口が誤る | 現状とVikunjaレビューへ更新する |
| DR-10 | 低 | Linux構築ガイドは作成済みだがCompose実体がない | サーバー準備後に手作業が増える | secretを含まないCompose例とenv例を追加する |

## upstream確認

- stable tag: `v2.3.0`
- stable task create: `PUT /api/v1/projects/{project}/tasks`
- main task create: `POST /api/v2/projects/{project}/tasks`
- stable task update: `POST /api/v1/tasks/{task}`
- Webhook signature: `X-Vikunja-Signature`、raw bodyに対するHMAC-SHA256 hex
- Webhook event: `event_name`、event data内のtask/project
- stable event middleware: retry 5回を設定。ただし受信側は配送保証へ依存せず、冪等処理と定期照合を維持する

## 維持する設計

- pj-generalは入口原文、AI候補、ユーザー判断、同期監査の正本。
- VikunjaはGO済み実行TODOの正本。
- upstream無改変で実機確認し、不足が観測された後にplugin / frontend fork / backend forkを選ぶ。
- forkは`rohto4/vikunja`に作成済みだが、現時点では差分を持たせない。

## 実装開始ゲート

- 本レビューのDR-01からDR-10を設計・準備資料へ反映する。
- LinuxサーバーでDocker Composeが実行できる。
- secretをリポジトリ外に作成できる。
- Vikunjaのpin済みrelease、API mode、project IDを確認できる。
- 受入テストの証拠保存先を用意する。
