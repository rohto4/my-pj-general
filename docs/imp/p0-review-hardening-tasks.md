# P0 仮完了レビュー待ちタスク表

> 完了済みの履歴タスク。現行判定は `docs/imp/p0-completion-audit-2026-07-12.md` を正本とする。

作成日: 2026-07-10

## 目的

P0 本デモ化完了後、ユーザーがレビューして「P0 仮完了」と判断できる状態まで硬化する。

P0 仮完了は、全外部連携・本AI・本認証の完成ではない。Web手入力、knowledge-vault import、Slack import payload、確認待ちキュー、GO / 編集 / 不要 / アーカイブ、管理画面、ダッシュボード、ガントが一貫した SQLite データでデモでき、ユーザーが次の判断を返せる状態を指す。

## 達成条件

| ID | タスク | 完了条件 | 状態 |
| --- | --- | --- | --- |
| P0-REVIEW-01 | 確認待ち候補を編集保存できるようにする | 詳細 pane で title / summary / todo / schedule / tags 等を編集し、SQLite に保存できる | 完了 |
| P0-REVIEW-02 | `編集してGO` の導線を作る | 編集後に `edited` または `approved` へ進める流れがある | 完了 |
| P0-REVIEW-03 | 管理画面の設定保存を最小実装する | source enabled、prompt enabled などの変更が SQLite に保存できる | 完了 |
| P0-REVIEW-04 | knowledge-vault import の重複・更新表示を改善する | imported / skipped / scanned と最終取り込み時刻が画面で分かる | 完了 |
| P0-REVIEW-05 | Slack import の実運用手順を用意する | connectorで読んだメッセージを `/api/import/slack` へ流す手順がある | 完了 |
| P0-REVIEW-06 | レビュー用確認観点を整理する | ユーザーが触る順番、期待結果、判断してほしい点が `docs/imp/user-tasks.md` にある | 完了 |
| P0-REVIEW-07 | P0仮完了レビュー前検証を通す | `pnpm check`、API、永続化、import、画面の主要導線を確認する | 完了 |

## 現時点のレビュー対象URL

```text
http://127.0.0.1:4173
```

## 現在の状態

P0 仮完了レビュー待ち。

ユーザーは `docs/imp/user-tasks.md` の「2026-07-10 P0 本デモレビュー手順」に従って、画面を触って確認する。

## 2026-07-10 実装メモ

- `PATCH /api/candidates/:id` を追加し、詳細 pane の編集フォームから title / summary / excerpt / todo / schedule / tags を保存できるようにした。
- 編集フォームには `保存` と `保存してGO` を置き、`edited` または `approved` へ進められる。
- `PATCH /api/admin/sources/:id` と `PATCH /api/admin/prompt-templates/:id` を追加し、source enabled と prompt enabled を SQLite に保存できるようにした。
- HTTP 経由で候補編集、source toggle、prompt toggle を確認済み。
- knowledge-vault import は imported / skipped / scanned と最終取り込み時刻を管理画面で確認できる。
- Slack `memo-ideas` は connector で確認し、現時点ではチャンネル参加メッセージのみで取り込み対象投稿なし。P0 は connector / 手動 payload を `/api/import/slack` に流す方式でレビューする。
- `docs/imp/user-tasks.md` にレビュー順序、期待結果、判断してほしい点を整理した。
- `pnpm check` と `/api/bootstrap` を確認済み。Ganttは固定サンプルを返さず、SQLite候補またはVikunja実行状態に日付がある行だけを返す。日付付きデータがない場合は空状態を表示する。
