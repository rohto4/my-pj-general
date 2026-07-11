# 次セッションの焦点

## 2026-07-11 現在

- HubからVikunja概要・直近タスクを読み取るAPIとダッシュボード表示を追加済み。
- HubのTasks側ナビ、確認待ち詳細、参考ガントからVikunjaへ遷移できるようにした。
- GO後はTasks側でタスク実行を完結し、Hubは候補・判断・連携状態を担当する一方向境界へ更新済み。
- Linux実機で概要APIと画面導線を確認し、Hub / Vikunjaのデザイン洗練まで実施済み。次はユーザーの微調整を受ける段階。

## 最優先

- ユーザーはVikunja設計レビューとLinuxサーバー準備を進める
- CodexはLinux待ちの間にadapterのunit/integration testを先行する。SQLite migrationは完了済み
- ユーザー判断待ちと Codex 側実装待ちを分けた状態を維持する
- P0 本デモ状態をレビュー可能に保つ
- SQLite 永続化、実入口 import、確認待ち操作、管理画面P0設定を壊さず前進する
- 必要なら UI 仕上げを継続するが、mock へ戻さない
- `docs/imp/hub-vikunja-ui-harmonization-tasks.md` の第1段階・第2段階を、実機導線確認後に進める

## Codex が進める具体タスク

1. P0 本デモ状態をユーザーが触った結果を反映する
2. SQLite schema を後続 PostgreSQL 移行しやすい形へ見直す
3. knowledge-vault import の重複判定と対象範囲を調整する
4. Slack `memo-ideas` に投稿が増えたら connector 経由で `/api/import/slack` payload に流す
5. 確認待ち詳細の編集項目、管理画面 P0 最小範囲、SQLite 継続利用可否のユーザー判断を反映する
6. `docs/imp/vikunja-integration-tasks.md` のGまでを確認し、設計正本は `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md` とする
7. 初回実機結合はVikunja `v2.3.0` / API v1へ固定し、`docs/spec/vikunja-integration-acceptance-tests-2026-07.md`で検証する

## 判断待ち

- 現時点で、P0 薄く実装 1 版の開始を止めるユーザー判断待ちはない。
- Slack の対象 channel は `memo-ideas`。
- Slack URL は `https://unibell4-dev.slack.com/archives/C0BG4TCPAUD`。
- Slack `memo-ideas` は 2026-07-10 時点で取り込み対象投稿なし。チャンネル参加メッセージのみ確認済み。

## 現在のブロッカー

- P0 本デモのレビュー開始を止めるブロッカーはない。
- Slack はアプリ本体に認証情報を持たせず、P0では connector / 手動 import payload 経路で扱う。
- Misskey はまだ mock data のまま。
- AI 整理結果は全件確認待ちでよい。
- P0 全体完了時点で、部分自動確定の条件を再設計する。
- 現在の `apps/web` は依存なしの Node 標準サーバ + Python 標準 `sqlite3` helper で動く。
- SQLite ファイルは `apps/web/data/p0.sqlite` にローカル生成され、git 管理外。
- Vikunjaはfork、upstream clone、設計レビュー、実機E2E、Compose/env雛形まで完了。Hub概要APIとTasks側導線の実Linux画面確認が次の検証単位である。
