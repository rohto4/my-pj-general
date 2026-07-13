# 2026-07-12 P0 UI / Vikunja fork 継続監査

## 実施内容

- `AGENTS.md`、`PROJECT.md`、主要P0タスク・判断・監査資料を再読込みした。
- HubをWQHD相当（2560 x 1440）で実ブラウザ撮影した。
- 通常ダッシュボードからAI相談の埋め込み本体を非表示にした。相談は `/chat` 独立画面とサイドウィンドウで提供する。
- Vikunja forkのdashboard実装をlint、単体テスト、production build、型検査で確認した。

## スクリーンショット

- 通常画面: `tmp/current-hub-wqhd-full.png`
- AI相談独立画面: `tmp/current-hub-chat-wqhd.png`

## UI所見

- 横断ダッシュボード、ガント、確認待ちキュー、作業者用、管理画面の縦順は維持されている。
- 横断ダッシュボードからガント先頭までを同一画面で確認でき、左側の入口別量・候補種類と右側の優先確認・判断ログの比率も崩れていない。
- 通常画面にAI相談の大きな空白を残すと一覧密度を落とすため、独立画面へ責務を寄せた。
- 画面ロード時のconsole errorは404が1件あり、既存の未接続Tasks側表示と合わせて、Vikunja公開URLを設定した実環境で再確認が必要。

## Vikunja fork品質ゲート

- `dashboardDate.test.ts`: 4件成功。
- production build: 成功。`ProjectDashboard` chunk生成を確認。
- fork差分2ファイルのESLint: エラー0、警告はVue既存ルールとmarkup整形。
- 全体型検査: upstream既存の `ProjectWrapper.vue`、`router/index.ts` 等の型エラーで失敗。今回の `ProjectDashboard.vue` / `dashboardDate.ts` に該当エラーはない。
- custom image / Linux起動: Windows側Docker未導入、Linuxはこの環境のSSH鍵認証が通らず未検証。

## 現在の判断待ち・ブロッカー

- ユーザー判断: HubのTasks側リンクを標準project URLからfork dashboard URLへ切り替えるか。
- ユーザー判断: Vikunja dashboardの30日カレンダーを標準ビュー入口にするか。
- 技術ブロッカー: Linux custom imageをbuild・起動するためのSSH鍵認証またはサーバー側実行環境。
- 非ブロッカー: upstream全体型検査の既存エラー。buildと今回差分のlint・unitは通過している。

## 保存状態

- dashboard実装をfork branchへ `7310f72d0` としてlocal commitした。
- GitHub pushはcredential providerの `SEC_E_NO_CREDENTIALS` で未実施。認証復旧が必要。

## 2026-07-12 継続確認

- Hub `http://127.0.0.1:4173/chat` と `/api/chat/bootstrap` は200、faviconも200で到達した。
- Hub標準テストはNode 13件、Python 3件、`check.ps1` が成功した。
- Vikunja frontendは、bundled Node runtimeをPATHへ追加して `dashboardDate.test.ts` 4件、対象lintエラー0、production build成功を再確認した。対象lintは警告62件で、upstreamのVue markup整形ルールに限られる。
- 全体typecheckはexit 2。新規dashboard/date実装ではなく、upstream由来の `ProjectWrapper.vue`、`router/index.ts` などの既存型エラーが残る。
- GitHub connectorは認証ユーザー `rohto4` と権限を確認できたが、`codex/pj-general-dashboard` branch作成で `403 Resource not accessible by integration` となった。local commit `7310f72d0` は保持している。
- Linux再接続は `unibell4@192.168.0.200` が `Permission denied (publickey,password)`、`universe` が名前解決失敗だった。
- `infra/vikunja/compose.example.yaml` に `VIKUNJA_IMAGE` 切替を追加し、stable imageを既定にしたままcustom imageのbuild / rollback手順を `docs/imp/vikunja-dashboard-fork-tasks.md` に記録した。
- 固定Ganttサンプルを除去したHubを再起動し、現在週起点の目盛りと日付付きデータなしの空状態をWQHDフルスクロールで撮影した。成果物は `tmp/current-hub-dynamic-gantt-full.png`。

## 2026-07-12 最新再検証

- Hubの回帰検証はNode 14件、Python 3件、`check.ps1` が成功した。`git diff --check` は改行コードの警告のみだった。
- Vikunja frontend forkはCodex bundled Nodeを明示して、`dashboardDate.test.ts` 4件、対象lintエラー0、production build、Workboxの静的ファイル生成を再確認した。
- 対象lintの警告62件は、新規dashboardのVue markup整形ルールが中心で、実行を止めるエラーではない。全体typecheckのupstream既存エラーとは分離して扱う。
- GitHub連携の認証ユーザーは `rohto4`、repositoryのpush権限は確認できたが、`codex/pj-general-dashboard` branch作成は再試行後も `403 Resource not accessible by integration` だった。
- WSL / DockerはこのWindows環境で利用できず、Linux `192.168.0.200` はSSH公開鍵認証失敗、`universe` は名前解決失敗だった。custom imageのbuild・起動・rollbackは未検証のまま残る。
