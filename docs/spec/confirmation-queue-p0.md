# P0 確認待ちキュー仕様

作成日: 2026-07-09

## 目的

この文書は、AI 整理結果をユーザーが確認し、`GO` / `編集` / `不要` / `アーカイブ` できる P0 確認待ちキューの最小仕様を定義する。

P0 では、すべての候補を確認待ちにする。部分自動確定はP1で判断実績を蓄積し、dry-runを通した後に再評価する。

2026-07-10 時点の本デモ状態では、確認待ち候補と判断ログは SQLite に永続化する。

## 参照 UI

- 主参照: `shadcn/ui Tasks example`
- 主参照: `Plane Intake / AI triage`
- 補助参照: `OpenProject Work Packages`

## 対象データ

確認待ちキューに並ぶのは、Hub SQLite の `candidates` に保存された確認対象である。AI相談由来だけでなく、Web手入力、Slack payload、knowledge-vault scanを含む。P0では独立したRaw入口イベント / 正規化イベントtableを持たず、`source`、`source_path`、本文抜粋、要約、発生時刻で出典を追跡する。

Raw入口イベント / 正規化イベントはP1以降の候補モデルであり、現行P0の一覧・保存形式ではない。詳しくは `docs/spec/intake-source-adapters.md` と `docs/data/p0-data-flow-2026-07.md` を正本とする。

## 一覧の最小列

| 列 | 表示内容 | 用途 |
| --- | --- | --- |
| Status | `pending` / `edited` / `approved` / `rejected` / `archived` | 作業状態を見る |
| Title | タイトル候補 | 何の候補かを一目で見る |
| Kind | `idea` / `consideration` / `concern` / `todo` / `schedule_candidate` | GO 後の作成先を判断する |
| Source | `web` / `slack` / `knowledge_vault` / `chat` | どこ由来かを見る |
| Tags | AI のタグ候補 | 分類の妥当性を見る |
| Confidence | AI の自信度 | 将来の自動化材料として見る |
| Missing | 不足項目 | 編集が必要か判断する |
| Occurred | 元データ上の発生時刻 | 古さと流れを見る |

## 詳細 pane

行を選択すると、右 pane または detail view で次を見せる。

- 元本文の抜粋
- AI 要約
- 関連リンク
- TODO 案
- 予定案
- 所要時間案
- GO 後に作られる object のプレビュー
- 元イベントへの内部参照
- source path / permalink

## フィルタ

P0 薄く実装 1 版では次を用意する。

| Filter | 値 |
| --- | --- |
| Status | `pending` / `edited` / `approved` / `rejected` / `archived` |
| Source | `web` / `slack` / `knowledge_vault` / `chat` |
| Kind | `idea` / `consideration` / `concern` / `todo` / `schedule_candidate` |
| Missing fields | あり / なし |
| Confidence | low / medium / high |

## 操作

| 操作 | 挙動 |
| --- | --- |
| `GO` | 現在の提案内容で Vikunja task を冪等に1件作る |
| `編集` | detail view で編集対象にする。P0 薄く実装 1 版では `edited` 状態にする |
| `不要` | `rejected` にする。Raw / 正規化イベントは追跡用に残す |
| `アーカイブ` | `archived` にして通常一覧から退ける |

P0 では一括 GO は必須にしない。誤確定を避け、1件ずつ体験を確認する。

操作結果は `candidates.status` と `decisions` に保存する。

## 失敗・復旧・照合

| 操作 | 失敗時に保持するもの | 利用者の次操作 | 照合根拠 |
| --- | --- | --- | --- |
| 書き入れ / 編集 / 不要 / アーカイブ | 成功応答を受けた操作だけ。画面は仮候補・仮ログを作らない | 理由を確認して再送する。成功後は画面を再読込する | HTTP応答、`bootstrap.log`、SQLite `decisions.note` のoperation ID |
| GO時のVikunja API失敗 | `approved` 判断と `sync_failed` の試行記録。候補本文と判断履歴は失わない | Vikunja設定・疎通を直して再試行またはreconcileする | `execution_links`、`sync_attempts`、`/api/observability` |
| webhook欠落 / 外部task削除 | candidate・decision・link履歴を削除しない | reconcileでmirrorを更新し、削除済みtaskは`detached`として表示する | `execution_task_state`、`sync_events`、`execution_links.sync_state` |

操作IDは編集、GO、不要、アーカイブのように判断を変更する送信だけに付与する。入口scanの成功・失敗は操作IDではなく `source_sync_runs` で追跡する。

## GO 後の作成先

P0 は kind にかかわらず Vikunja の実行 task を作る。kind は候補分類として保持し、IdeaCard や Calendar event の別 object はまだ作らない。

## 自動確定の扱い

P0 薄く実装 1 版では、AI の confidence が高くても自動確定しない。

P1のdry-runでは、次のような条件を組み合わせて部分自動確定を検討する。

- `source_type`
- `candidate_kind`
- `confidence`
- `missing_fields` の有無
- タグ候補の安定度
- 過去のユーザー GO / 修正履歴

## 検証データ方針

本流は mock 候補を持たない。API test は一時 SQLite に検証候補を作り、実DBは実入口から取り込んだ候補だけを保持する。

## 明示承認済みの洗い替え

候補品質を改訂して既存の実行データを作り直す場合だけ、管理API `POST /api/admin/rebuild-knowledge-vault-candidates` を使う。この操作は通常の候補削除・再取込ではない。

1. 対象Vikunja Projectの全taskを削除する。
2. 成功した場合だけHubの`candidates`、`candidate_tags`、`decisions`、`execution_links`、`execution_task_state`、`sync_attempts`、`sync_events`、`source_sync_runs`を削除する。
3. `sources.last_imported_at`を空に戻し、新しい候補化規則でknowledge-vaultを直ちに再scanする。

設定、タグマスタ、prompt template、AI相談履歴は候補・実行の監査履歴ではないため保持する。外部taskの削除に失敗した場合はHubを削除せず失敗を返す。再scan後に作られる同期runは、空にした履歴の後の新しい開始記録である。

## 回帰・受入根拠

- 判断操作、operation ID、成功後の表示保持、仮候補を作らない境界は `apps/web/test/api.test.mjs` を自動根拠にする。
- GO、Webhook、reconcile、外部task削除は `docs/spec/vikunja-integration-acceptance-tests-2026-07.md` と `apps/web/test/api.test.mjs` を併用する。
- 実データを変更する操作と幅別の画面受入は `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` の対象IDで別管理する。自動回帰が通っても実機受入済みとは扱わない。

## 関連文書

- `docs/spec/ai-assisted-registration-flow.md`
- `docs/spec/intake-unified-event-model.md`
- `docs/spec/intake-source-adapters.md`
- `docs/spec/hub-ui-interaction-contract-p0.md`
- `docs/spec/vikunja-integration-contract-2026-07.md`
- `docs/ops/p0-operations-runbook-2026-07.md`
- `docs/candi-ref/ui-reference-sources-for-initial-prototype.md`
