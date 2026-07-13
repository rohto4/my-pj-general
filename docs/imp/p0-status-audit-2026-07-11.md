# P0・データ連結・導線連結 状態監査

> 履歴監査。現行判定は `docs/imp/p0-completion-audit-2026-07-12.md` を正本とする。

監査日: 2026-07-11
対象: Hub、SQLite、入口、確認待ち、Vikunja実データ連結、Tasks導線

## 結論

- HubのP0本デモ、SQLite永続化、実入口、確認待ち操作、管理画面最小範囲は実装済み。
- HubからVikunjaへのGO登録、Hubでの概要読取、Tasks側URL導線、Webhook / 再照合による状態ミラーも実装・実機確認済み。
- Hub / P0 の技術ブロッカーは現時点でない。
- 残っているP0作業は、ユーザーの実画面受入と必要な微調整である。
- Vikunja frontendのスクロール式dashboard、今後30日カレンダー、upstream追随を考慮したfork差分は、既存P0連結の後続拡張として進める。

## 状態マトリクス

| 領域 | 状態 | 根拠・実装位置 | 残り |
| --- | --- | --- | --- |
| Web書き入れ口 | 完了 | `apps/web/app.js`, `apps/web/server.mjs` | ユーザー操作確認 |
| knowledge-vault import | 完了 | `apps/web/db_tool.py` の import 処理 | 対象範囲・重複判定の将来調整 |
| Slack memo-ideas | P0経路完了 | connector / 手動payloadを `/api/import/slack` へ渡す | 実投稿が増えた時の運用確認 |
| Misskey | P0範囲外 | sourceを無効状態で保持 | 実connectorは後段 |
| SQLite候補・判断 | 完了 | `apps/web/data/p0.sqlite`, `apps/web/db_tool.py` | PostgreSQL移行は後段 |
| 確認待ち操作 | 完了 | GO / 編集 / 不要 / アーカイブ、`decisions` | ユーザー受入 |
| 管理画面P0 | 完了 | source / tags / roles / automation / scopes / prompts | ユーザー受入 |
| Hub概要 | 完了 | `GET /api/integrations/vikunja/overview` | 表示微調整 |
| Hub -> Tasks GO | 完了 | `POST /api/candidates/:id/execution` | 二重登録・失敗表示の回帰確認 |
| Tasks -> Hub状態反映 | 完了 | Webhook / reconcile、`execution_task_state` | 運用workerは後段 |
| Hub -> Tasks導線 | 完了 | ダッシュボード・確認待ち詳細・Tasks連携予定表示のURL | ユーザー受入 |
| Vikunja fork dashboard | 実装中 | `G:\devwork\clone-dir\vikunja-upstream`、`docs/imp/vikunja-dashboard-fork-tasks.md` | custom image、Linux起動、Hub主リンク判断 |
| Hub / Tasksデザイン調和 | 第1・2段階の実装完了 | `docs/imp/hub-vikunja-ui-harmonization-tasks.md` | 並列画面の最終微調整 |

## 現時点のユーザー確認事項

1. P0の画面順序・情報密度・文字サイズで日常利用できるか。
2. GO後に期限、担当、進捗、完了をTasks側で完結する一方向境界でよいか。
3. Tasks側dashboardを標準ビューの入口にすること、既存List / Table / Kanban / Ganttへリンクを残すことに異論がないか。
4. カレンダーの初期期間を「今日から30日」とすること、日付なしtaskを別一覧に出すことがよいか。
5. Misskey実接続、AI部分自動GO、定期workerをP0外として扱うことでよいか。

## 技術ブロッカー

### 解消済み

- Linux上のVikunja起動。
- runtime API token、project ID、Hub側接続。
- GOによる実task作成。
- Webhook署名・冪等保存・状態反映。
- Webhook欠落時の再照合。
- Hub概要APIとブラウザー向け公開URLの分離。

### 現在の候補ブロッカー

- Vikunja forkのfrontend build成果物を、既存のLinux実行方式へどう配信するか。ソース実装よりもcustom image build / deployが先に検証対象。
- upstream更新時に `router`、`ProjectWrapper`、`ProjectView`、CSS、frontend testを追随する保守コスト。
- Task一覧のページング仕様。dashboardで全taskを扱う場合、既存APIのページングを壊さずに取得する必要がある。

これらはHub/P0連結を止めるブロッカーではなく、Vikunja frontend forkへ進む際の実装ゲートである。

## 非P0の残作業

- Vikunja frontend forkのcustom image、Linux起動、Hub主リンク切替判断。
- Linux `systemd timer` による6時間ごとの入口回収。
- PostgreSQL、Redis / BullMQへの移行。
- Misskey adapter。
- 認証、複数ユーザー、細かな権限制御。
- AI部分自動GO条件の確定。
- HubとTasks間の候補本文・判断の双方向同期。

## 参照正本

- 現行ゴール・データ境界: `docs/imp/current-goal-and-data-structure-brief-2026-07-11.md`
- P0タスク: `docs/imp/p0-production-demo-tasks.md`
- 実装待ち: `docs/imp/imp-tasks.md`
- ユーザー確認: `docs/imp/user-tasks.md`
- ユーザー判断: `docs/imp/user-judge.md`
- データ設計: `docs/data/vikunja-integration-data-design-2026-07.md`
- 結合アーキテクチャ: `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`

## 2026-07-12 継続監査追記

- Hubの実ブラウザWQHD撮影を行い、通常画面からAI相談の大きな埋め込み空白を除去した。相談は `/chat` とサイドウィンドウへ分離した。
- 撮影成果物は `tmp/current-hub-wqhd-full.png` と `tmp/current-hub-chat-wqhd.png`。
- Vikunja fork dashboardはbranch、route、ページング、集計、30日表示、未日付一覧、ProjectWrapper導線、日付単体テスト、production buildまで確認済み。
- HubのTasks連携予定表示から固定Ganttサンプルを除去し、SQLite候補・実行状態の日付付きデータと現在週起点の週目盛りだけを表示するようにした。日付付きデータがない場合は空状態を表示する。
- 残件はユーザー受入、dashboard URLをHub主リンクにする判断、Linux custom imageのbuild / 起動、upstream全体型検査の既存エラーである。
