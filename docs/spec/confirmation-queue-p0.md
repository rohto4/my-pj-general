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

確認待ちキューに並ぶのは `AIRegistrationCandidate` 相当の AI 整理結果である。

Raw 入口イベントや正規化イベントは内部参照として保持し、一覧では必要な分だけ表示する。

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

## 関連文書

- `docs/spec/ai-assisted-registration-flow.md`
- `docs/spec/intake-unified-event-model.md`
- `docs/spec/intake-source-adapters.md`
- `docs/candi-ref/ui-reference-sources-for-initial-prototype.md`
