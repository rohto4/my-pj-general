# 実装待ち

## 現在の状態

- 要件整理と P0 設計書作成が進行中。
- P0 本デモ状態は `apps/web` に作成済み。
- SQLite 永続化、Web 手入力、knowledge-vault import、Slack import payload、確認待ち操作、管理画面 P0 設定、ダッシュボード、ガント補助表示は同じ SQLite データで動く。
- 現在は P0 仮完了レビュー待ち。
- ユーザー判断待ちは `docs/imp/user-judge.md` と `docs/imp/user-tasks.md` を正本にする。
- 完了済みの作業は `docs/imp/imp-comp.md` を正本にする。

## Codex が進められるタスク

- P0 本デモ状態をユーザーレビュー結果に合わせて調整する
  - 正本: `docs/imp/p0-production-demo-tasks.md`
  - レビュー硬化: `docs/imp/p0-review-hardening-tasks.md`
  - 初手: `docs/imp/user-tasks.md` のレビュー結果を受け、SQLite schema、確認待ち詳細、管理画面、import 対象を調整する
  - 2026-07-10 追加: `docs/imp/p0-sqlite-completion-tasks.md` に、画面再配置、モック排除、管理最小範囲の SQLite 化を記録した
- Vikunja を外部 TODO 実行基盤として検証・接続する
  - 採用判断: `docs/imp/user-judge.md` の `UJ-VIKUNJA-01`
  - 比較正本: `docs/candi-ref/vikunja-fork-plugin-assessment-2026-07.md`
  - upstream 無改変の自己ホスト、API token、Webhook を用意する。接続先URLを SQLite 設定へ保存し、ダッシュボードの主導線を Vikunja TODO へ切り替える。
  - 初期は `GO -> Vikunja task作成` の一方向連携に限り、Webhook受信と定期照合による状態反映、双方向同期は別タスクに分離する。
  - backend plugin は追加API・イベント処理が必要になった場合だけ導入する。UI変更が必要になった場合だけ fork を判断する。
  - ガントは Vikunja TODO 内の副次ビューとして使い、pj-general に外部ガント専用導線は置かない。
- Linux 常設サーバー向けに定期入口同期 worker を導入する
  - 設計正本: `docs/arch/linux-periodic-intake-architecture.md`
  - 初期実装: `workers/sync` を切り出し、`systemd timer` から6時間ごとに `oneshot` 実行する
  - 完了条件: knowledge-vault、Slack、Misskey の source adapter が冪等に候補化でき、sourceごとの結果・失敗・最終成功時刻を確認できる
  - 後続: PostgreSQL、Redis / BullMQ、Vikunja TODO 同期
- 設計書内に混ざった `imp-wait` / `imp-task` 的な進行管理記述を `docs/imp/` 系へ分離する
  - 対象: `docs/spec/*`、`docs/product/*`、`docs/data/*` の後続設計、未決、実装待ちに相当する記述
  - 方針: 仕様本文には要件・設計判断だけを残し、実装待ち / 判断待ち / 次アクションは `docs/imp/imp-*` または `docs/imp/user-*` に移す
- P0 薄く実装 1 版をユーザーが触った後の調整を反映する
  - 画面密度
  - 確認待ちキューの列
  - GO / 編集 / 不要 / アーカイブの操作名
  - TODO主導線とガント補助表示の切り分け
- P0 薄く実装 1 版を Next.js / shadcn/ui へ移行するか判断する
  - 現在は依存なし静的プロトタイプ
  - Node.js PATH 整備後に本来の `Next.js + shadcn/ui` へ移す候補

## ユーザー判断後に進めるタスク

- 現時点で、P0 薄く実装 1 版の開始を止めるユーザー判断後タスクはない。

## 後で進めるタスク

- リポジトリ名、製品名、主要ロール名を確定する
- `goose` 単独追随の更新手順を文書化する

## 後回しタスク

- キャパ管理の詳細設計
- マルチエージェント開発用の別PJ土壌を作る
- Codex / MiMo / GLM の互換運用方針を別PJで整理する
- MCP を軸にしたマルチエージェント接続方針を別PJで評価する
