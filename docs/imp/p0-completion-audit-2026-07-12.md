# P0正式完了監査 2026-07-12

## 結論

P0のバックエンド・連携契約は正式完了と判定する。ただし、フロント画面の全操作受入とHub/Vikunjaの編集責務の説明は追加P0として未完了である。

Hub の必須導線、SQLite永続化、実入口、ユーザー確認、Vikunja実行、状態反映、AI相談、管理設定が実装され、契約回帰とLinux実機E2Eの両方で確認できた。P0外の常設worker、Misskey、Calendar、認証、PostgreSQL、部分自動確定、fork配信運用はP1候補へ分離する。

## P0の正式スコープ

```text
Web / knowledge-vault / Slack payload / AI相談
  -> Hub候補 pending
  -> 確認待ちで編集・GO・不要・アーカイブ
  -> GO時にVikunja taskを冪等作成
  -> Webhook / 再照合で完了・期限・担当・進捗をmirror
```

Misskey実接続とGoogle Calendarは、旧設計のP0表記を廃止しP1評価対象とする。

## 要件別判定

| 要件 | 判定 | 証拠 |
| --- | --- | --- |
| Web書き入れ | 完了 | `/api/candidates`、SQLite再読込、確認待ち表示 |
| knowledge-vault | 完了 | 実Markdown scan、hash dedupe、19件の実候補 |
| Slack `memo-ideas` | P0経路完了 | connector / 手動payload API、空payloadをmockしない |
| AI相談 | 完了 | `/chat`、drawer、SQLite履歴、読取tool、確認付きpending化、Ollama実接続歴 |
| 確認待ち | 完了 | 編集、保存、保存してGO、GO、不要、アーカイブ、判断記録 |
| 管理 | 完了 | source、tag、role表示、AI方針、scope、promptのSQLite操作 |
| GO -> Vikunja | 完了 | 実candidate `KV-e378384856`、task `#1`、二重作成なし |
| Vikunja -> Hub | 完了 | 署名Webhook、冪等event、再照合、完了・期限・担当・priority反映 |
| Tasks概要・導線 | 完了 | project概要、件数、直近task、Tasks URL、失敗時縮退 |
| Tasks連携予定表示 | 完了 | 固定sampleを除去し、日付付きSQLite / mirror dataだけを表示 |
| UI本流 | 完了 | Listening Lounge、1280 / 1920px、横overflow 0、構造角丸監査 |
| Vikunja fork UI | P0成果完了 | `codex/pj-general-dashboard`、commit `325bc5475`、14状態の実データ監査 |

## 検証証跡

### 2026-07-12 現行Hub回帰

- `apps/web/check.ps1`: 成功
- Node API / UI contract: 14 / 14成功
- Python adapter unit: 3 / 3成功
- 一時SQLite・擬似Vikunja・擬似LLMを使用し、実DBを変更せず検証
- 実DB読取: sources 5、candidates 19、pending 19、chat messages 4

### Linux実機E2E

- Vikunja stable `v2.3.0` / API v1
- 実候補GO、task作成、同一候補再GO時の二重作成防止
- 署名Webhookと再照合
- taskの未完了・完了、期限、担当、priorityのmirror
- 再起動、backup / restore
- 詳細: `docs/imp/vikunja-integration-verification-2026-07-11.md`

### Vikunja fork

- branch: `codex/pj-general-dashboard`
- final local commit: `325bc5475`
- unit scope: 48 files / 1065 tests成功
- Stylelint: error 0
- production build: 成功
- 1280px / 1920px、home / dashboard / list / sort / filter / task detail / table / kanban / ganttを実データ監査
- 詳細: `tmp/ui-review/vikunja-listening-lounge/README.md`

全体typecheckのupstream既存エラーと、E2Eを除外しない生VitestがPlaywright specを誤収集する問題は、今回の追加差分の失敗ではないためP0完了条件から分離する。

## P0監査時点の実DBスナップショット

実DBにはknowledge-vault由来のpending候補19件があり、判断0件、execution link 0件である。実行契約の実機証跡は別Linux環境で取得済みだが、日常運用の判断・GO実績はまだ蓄積されていない。この事実から、P1は大型基盤移行より常設運用と観測を優先する。

## 2026-07-12 Linux最新スナップショット

再配信・再起動後のLinux実DBでは、Hub candidates `19`、decisions `2`、execution links `2`、Vikunja tasks `2`を確認した。backup/restore hashも一致し、データ消失は確認されなかったため再インポートは行っていない。

## 残存リスクとP1送り

| 項目 | P0影響 | 扱い |
| --- | --- | --- |
| Hub / Vikunja / Ollamaが現在停止中 | なし | 起動時にrunbookで確認 |
| forkのGitHub push未完了 | なし | P1の配信・upstream追随 |
| fork custom imageのLinux切替未完了 | なし | P1のblue/green配信PoC |
| Slack実投稿がまだない | なし | 最初の実投稿でP1運用確認 |
| 実DBのGO実績がない | なし | P1の運用指標として蓄積 |
| Misskey / Calendar未接続 | なし | P1候補評価 |
| 認証なし・単一利用者 | なし | 二人目を招く前にP1/P2で実装 |

## 起動入口

- Hub既定: `http://127.0.0.1:4173/`
- AI相談: `http://127.0.0.1:4173/chat`
- `4175` はテーマ比較時の一時ポートであり、恒久既定ではない。
- Vikunjaは環境ごとの `VIKUNJA_PUBLIC_URL` を正本とする。

運用・backup・rollbackは `docs/ops/p0-operations-runbook-2026-07.md` を参照する。

## 2026-07-12 フロント再評価

この監査の「UI本流完了」は、テーマ・レイアウト・主要API結合の完了を指し、表示されたすべての項目がHubから編集できることを意味しない。Tasks概要とガントは現在「Vikunja側で管理する読み取り導線」であり、Hub候補・判断の編集とは責務が異なる。

以下は追加P0として扱う。

- 表示されたbutton / link / formの全数操作監査
- 無効リンクと未接続状態の理由・再試行導線
- Hub編集対象とVikunja編集対象の画面内説明
- 最新DB/APIフィールドのフロント反映
- 主要画面の実操作受入と4K縦3分割相当の確認

詳細: `docs/imp/p0-frontend-completion-tasks-2026-07-12.md`
