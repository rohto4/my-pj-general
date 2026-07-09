# 実装待ち

## 現在の状態

- 要件整理と P0 設計書作成が進行中。
- まだアプリ実装には入っていない。
- ユーザー判断待ちは `docs/imp/user-judge.md` と `docs/imp/user-tasks.md` を正本にする。
- 完了済みの作業は `docs/imp/imp-comp.md` を正本にする。

## Codex が進められるタスク

- 設計書内に混ざった `imp-wait` / `imp-task` 的な進行管理記述を `docs/imp/` 系へ分離する
  - 対象: `docs/spec/*`、`docs/product/*`、`docs/data/*` の後続設計、未決、実装待ちに相当する記述
  - 方針: 仕様本文には要件・設計判断だけを残し、実装待ち / 判断待ち / 次アクションは `docs/imp/imp-*` または `docs/imp/user-*` に移す
- 画面構成仕様を作る
  - 横断ダッシュボード
  - 書き入れ口 / 作成口
  - 管理画面
  - 実績 / 履歴参照
  - 作業者用 / タスクサマリページ
- ガント MVP 仕様を作る
  - P0 に入れる表示範囲
  - TODO / ScheduleCandidate との接続
  - OpenProject / Leantime から借りる範囲
- `docs/spec/classification-tag-master.md` を作る
  - タグマスタの初期分類
  - AI が選ぶタグとユーザーが編集するタグの境界
- `docs/spec/role-and-permission-initial.md` を作る
  - 自分中心
  - 外部協力者はスケジュール閲覧中心
  - 将来ロールは仮置き
- `docs/spec/prompt-template-management.md` を作る
  - Codex 起動支援用テンプレートの管理
  - `pj-general-derived` などの初期テンプレート
- `docs/spec/intake-source-adapters.md` の下書きを作る
  - Web / Slack / Misskey / knowledge-vault の adapter 責務
  - ただし Slack / knowledge-vault の回収対象範囲はユーザー判断待ちとして残す

## ユーザー判断後に進めるタスク

- `UJ-01` 後: Slack / knowledge-vault 回収対象範囲を反映した `intake-source-adapters` の確定版を作る
- `UJ-02` 後: AI 自動分別をどこまで自動確定させるかを `ai-assisted-registration-flow` に反映する
- `UJ-03` 後: 確認待ちキューの表示項目と GO 操作を画面仕様へ反映する

## 後で進めるタスク

- リポジトリ名、製品名、主要ロール名を確定する
- `goose` 単独追随の更新手順を文書化する

## 後回しタスク

- キャパ管理の詳細設計
- マルチエージェント開発用の別PJ土壌を作る
- Codex / MiMo / GLM の互換運用方針を別PJで整理する
- MCP を軸にしたマルチエージェント接続方針を別PJで評価する
