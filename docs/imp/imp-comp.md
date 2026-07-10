# 完了記録

## 2026-06-23

- `G:\devwork\pj-general` を新PJの仮ルートとして初期化
- 大規模PJ向けの基本ディレクトリ構造を作成
- `obsidian-set` から `commands/` と `.agents/skills/` を流用
- `knowledge-vault` のテンプレート群を `docs/setting/templates/knowledge-vault/` にコピー
- `obsidian-set` / `knowledge-vault` / `my-LLMwiki` の agent / project / readme テンプレートを `docs/setting/bootstrap-sources/` に保存
- 次走向けに OSS 選定バックログと地盤方針を作成
- 高スター repo として `aaif-goose/goose`, `PrefectHQ/fastmcp`, `modelcontextprotocol/servers` を `G:\devwork\clone-dir` に clone
- `goose` の `AGENTS.md` と `.codex/skills` 参照構造を `docs/setting/bootstrap-sources/aaif-goose-goose/` に保存
- `fastmcp-client-cli` skill を `pj-general/.agents/skills/` に取り込み
- `fastmcp` の運用指示と `modelcontextprotocol/servers` の README を bootstrap source に保存
- Codex 専用運用土台の upstream は `goose` 単独追随とし、他 repo は参考用として保持する方針に変更
- 今回の判断を `G:\knowledge-vault` 配下の既存カテゴリへ反映する前提を確定

## 2026-07-02

- `G:\knowledge-vault\knowledge-vault-write-policy.md` を中央正本として作成し、PJ 側から参照する運用へ変更
- `G:\knowledge-vault\memory\l1-triggers.md` に knowledge-vault 記載方針への想起入口を追加
- `pj-general` の `AGENTS.md` に、knowledge-vault 記載前に中央 policy を読むルールを明文化
- Mermaid 図作成用 skill `.agents/skills/mermaid-diagram-style/` を作成
- 技術スタック比較表と技術概念表を作成
- P0 全体要約ワークフロー図と P0 データフロー図を作成
- P0 統一入口イベントモデルを作成
- P0 AI 整理・登録支援フローを作成
- P0 初期業務オブジェクトモデルを作成
- P0 Google Calendar 連携フローを作成
- P0 Codex プロジェクト開始支援フローを作成
- Mermaid 図でユーザー操作点と自動処理点を見た目上区別できるように修正
- ユーザー判断待ちを整理し、Google Calendar、外部協力者表示、ガント、キャパ、Codex 起動支援の判断を反映
- `docs/guide/docs-management-rules.md` を作成し、docs 配下の正本、同期先、更新トリガー、更新漏れパターンをマトリクス化
- `docs/guide/docs-management-matrix-result-diagram.md` を作成し、docs 管理マトリクスの結果を Mermaid 図で可視化
- `AGENTS.md` / `PROJECT.md` / `chat-init.md` / `docs/README.md` に docs 相互更新ルールへの参照と基本原則を追記
- 横断再利用できる docs 正本・同期ルールを `G:\knowledge-vault\knowledge\dev\docs-source-of-truth-update-rules.md` に反映
- `docs/guide/docs-management-rules.md` を docs update policy 相当に拡張し、タスク整理、進捗、判断待ち発生、判断待ち解消、完了、handoff 作成のタイミング別更新判断表を追加
- `AGENTS.md` は詳細表を重複させず、PJ docs 更新判断は `docs/guide/docs-management-rules.md`、横断ナレッジ更新判断は `G:\knowledge-vault\knowledge-vault-write-policy.md` を参照する形に整理
- 新PJへ引き継ぐ最小ルールセットを `docs/guide/docs-management-rules.md` に追加
- `.agents/README.md` を追加し、`.agents/` 配下へ docs 更新判断表を重複コピーしない方針を明記
- `chat-init.md` / `AGENTS.md` / `docs/guide/docs-management-rules.md` / `G:\knowledge-vault\knowledge-vault-write-policy.md` の「横断価値のある知見だけ」系の表現を改め、各作業ポイントで knowledge-vault への反映要否を評価する方針へ統一
- `chat-init.md` を削除し、毎チャット共通ルールは `AGENTS.md`、セッション固有 handoff は `docs/diary/*` / `docs/imp/*` に集約する方針へ変更
- `docs/guide/docs-management-matrix-result-diagram.md` の「更新漏れリスク」図を、イベント発生から正本更新、進行管理、入口同期、handoff、knowledge-vault 評価、終了前チェックまでの仕組み図へ差し替え
- `docs/guide/docs-management-matrix-result-diagram.md` の色分けを、入力口は青、出力先は赤、判断・ルール・確認などその他はグレーに統一

## 2026-07-09

- `PROJECT.md` からタスク、今回の到達目標、参照元一覧、次走テーマなどの履歴・作業管理情報を削除
- `PROJECT.md` の責務を、PJ 固有の目的、スコープ、正本関係、恒久的な構造、採用済み重要判断に限定する形へ整理
- `AGENTS.md` に、PROJECT.md へタスク、進捗、次走テーマ、セッション履歴、判断材料の生ログ、参照元一覧を書かない実行ルールを追加
- `docs/guide/docs-management-rules.md` に、PROJECT.md を履歴置き場にしない禁止事項と配置先の分離ルールを追加
- `AGENTS.md` に、コンテキスト自動圧縮、セッション移動、handoff 受領、要約コンテキストからの再開を検知した場合、通常回答や作業継続より前に初期化ファイル群を再読み込みするルールを明記
- `docs/guide/docs-management-rules.md` に、圧縮後要約だけで再開しないためのタイミング別更新判断と更新漏れ防止パターンを追加
- Codex 自動圧縮の公式 manual 調査、`compact_prompt` override の保留判断、`PreCompact` / `PostCompact` / `SessionStart compact` hook 優先案、今回編集した PJ ファイルと期待動作を `G:\knowledge-vault\knowledge\dev\codex-auto-compact-recovery-design.md` に現時点版として保存
- `C:\Users\unibe\.codex\AGENTS.md` に compact 復帰の最優先ルールを追記
- `C:\Users\unibe\.codex\hooks.json` と `C:\Users\unibe\.codex\hooks\post_compact_reminder.ps1` / `session_start_compact_reminder.ps1` を作成し、`PostCompact` と `SessionStart compact` で復帰 reminder / log を生成する設定を追加
- `C:\Users\unibe\.codex\config.toml` で Memories を有効化し、compact 復帰時の補助記憶として使う設定を追加
- hook script を手動実行し、`C:\Users\unibe\.codex\compact-recovery-reminder.md` と `C:\Users\unibe\.codex\logs\compact-recovery.log` の生成を確認
- 初期プロトタイプ向けの UI 参考資料を `docs/candi-ref/ui-reference-sources-for-initial-prototype.md` に整理し、既存調査での `Plane` / `OpenProject` / `Leantime` / `shadcn/ui` の役割分担を画面別に落とし込んだ
- `UJ-01` / `UJ-02` / `UJ-03` のユーザー判断を `docs/imp/user-judge.md`、`docs/imp/user-tasks.md`、`docs/imp/next-session-focus.md` に反映し、P0 薄く実装 1 版の開始を止める判断待ちがない状態に整理した
- Slack / knowledge-vault / Misskey / Web の入口別 adapter 仕様を `docs/spec/intake-source-adapters.md` として作成した
- P0 確認待ちキュー仕様を `docs/spec/confirmation-queue-p0.md` として作成し、全件確認待ち、GO / 編集 / 不要 / アーカイブの最小操作を固定した
- knowledge-vault の現在構成と P0 暫定取り込み対象を `docs/candi-ref/knowledge-vault-current-structure-for-intake.md` に整理した
- Slack 対象チャンネルを `memo-ideas`（`https://unibell4-dev.slack.com/archives/C0BG4TCPAUD`）に確定し、knowledge-vault の `inbox/` を P0 取り込み対象へ追加した
- P0 薄く実装 1 版のタスク表を `docs/imp/p0-thin-implementation-tasks.md` に作成した
- P0 画面構成仕様を `docs/spec/screen-structure-p0.md`、ガント MVP 仕様を `docs/spec/gantt-mvp-flow.md` として作成した
- `apps/web` に依存なし静的プロトタイプを作成し、書き入れ口、確認待ちキュー、横断ダッシュボード、作業者用 / タスクサマリ、ガント表示、管理画面の最小範囲を mock data で触れる状態にした
- root `package.json`、`pnpm-workspace.yaml`、`apps/web/package.json`、`apps/web/server.mjs`、PowerShell wrapper を追加し、`pnpm check` と `pnpm dev` で確認できるようにした
- `pnpm check`、`pnpm dev`、HTTP 200 応答、主要画面文言の表示を確認した
- P0 薄く実装 1 版に対する初回フィードバックを反映し、表示順を `横断ダッシュボード -> ガント表示 -> 確認待ちキュー -> 作業者用 / タスクサマリ -> 管理画面` に変更、書き入れ口を右 drawer 化、ガントを週メモリ付き日本語サンプルに変更、横断ダッシュボードの指標を増やし、確認待ちキュー詳細 pane と操作ボタン幅を調整した
- P0 本デモ化タスク表を `docs/imp/p0-production-demo-tasks.md` として作成し、SQLite 永続化と実入口を持つデモ可能な P0 へ進める方針を固定した
- 横断ダッシュボードを左サマリ列 + 右側処理フロー / 優先確認 / 判断ログへ再配置し、WQHD でガント先頭まで見える密度に調整した
- 確認待ちキュー詳細 pane の `AI要約`、`抜粋`、`TODO案`、`予定案`、`参照元`、`GO後プレビュー` にラベル色と本文色の差を付けた
- 操作可能、選択中、操作不能の見た目をブルー系の明暗・濃淡で整理し、不要な角丸を減らした
- 管理画面の最小範囲を P0 状態へ拡張し、入口設定、タグマスタ、ロール表示、AI確定方針、プロンプトテンプレート、取り込み対象を表示する構成にした
- `apps/web/db_tool.py` を追加し、Python 標準 `sqlite3` で `apps/web/data/p0.sqlite` を初期化・操作する構成にした
- `apps/web/server.mjs` に `/api/bootstrap`、`/api/candidates`、`/api/candidates/:id/status`、`/api/import/knowledge-vault`、`/api/import/slack` を追加した
- Web 書き入れ口から候補を SQLite に保存し、確認待ち操作の `GO` / `編集` / `不要` / `アーカイブ` を `decisions` に永続化するようにした
- knowledge-vault の `inbox`、`records`、`tasks`、`memory` から Markdown を読み、`KV-*` 候補として SQLite に取り込めるようにした。検証では10件を取り込み、候補合計16件になった
- Slack `memo-ideas` は connector で読み取り、現時点で取り込み対象メッセージがないことを確認した。P0では `/api/import/slack` へ connector / 手動 import payload を渡す経路を用意した
- `pnpm check` を強化し、`app.js`、`server.mjs`、SQLite bootstrap を確認するようにした
- `pnpm check`、API bootstrap、Web候補作成、状態更新、knowledge-vault import、Slack import test、WQHD遅延スクリーンショットを確認した
- `docs/spec/classification-tag-master.md`、`docs/spec/role-and-permission-initial.md`、`docs/spec/prompt-template-management.md` を作成し、管理画面P0最小範囲の仕様正本を補完した
- P0仮完了レビュー待ちタスク表 `docs/imp/p0-review-hardening-tasks.md` を作成した
- 確認待ち詳細 pane に編集フォームを追加し、title / summary / excerpt / todo / schedule / tags を SQLite に保存できるようにした
- `保存` と `保存してGO` を追加し、編集後に `edited` または `approved` へ進められるようにした
- 管理画面の source enabled と prompt template enabled を SQLite に保存する API と UI トグルを追加した
- knowledge-vault import の imported / skipped / scanned と最終取り込み時刻を管理画面で見られるようにし、P0レビュー手順に反映した
- Slack `memo-ideas` は connector で読み取り、現時点で取り込み対象投稿がないことを確認した。P0では connector / 手動 payload を `/api/import/slack` へ流す方式としてレビュー手順に残した
- P0 仮完了レビュー待ちタスク `P0-REVIEW-01` から `P0-REVIEW-07` を完了に更新した
- P0 仮完了レビュー前検証として `pnpm check` と `/api/bootstrap` を確認した。API は candidates 16 件、knowledge-vault 由来 10 件、ganttTasks 4 件、sources 4 件、promptTemplates 3 件を返す
# 2026-07-10 P0 SQLite 完結・画面再配置

- 横断ダッシュボードから8数値を撤廃し、入口別量・候補の種類・処理フロー・優先確認・判断ログの配置を再構成した。
- 確認待ちキューを詳細左・一覧右へ反転した。
- コピー操作を実クリップボード書き込みへ変更し、連続実行できるようにした。
- ロール、AI方針、knowledge-vault対象、タグを SQLite 保存の管理操作へ移した。
- 初期モック候補、空 Slack payload、クライアント側の通信失敗フォールバックを除去した。
- `apps/web/test/api.test.mjs`、`apps/web/check.ps1`、`/api/bootstrap` を確認した。

# 2026-07-10 Leantime 実行基盤・UI参照調査

- Leantime の TODO、subtask、dependency、list / table / kanban / calendar / gantt、goal、dashboard、timesheet、API / plugin / MCP の現行機能を公式資料で確認した。
- `docs/candi-ref/leantime-adoption-and-ui-reference-2026-07.md` に、UI参照・外部連携・fork / 改変の3方式、AGPLv3注意点、pj-generalとの責務境界、画面別の参照対象、Linux配置前提を整理した。
- 実行基盤の判断待ちを `UJ-GANTT-01` から `UJ-LEANTIME-01` に更新し、推奨を「Leantime独立自己ホスト + GO済み候補の一方向TODO連携」とした。OpenProject は横断計画・大規模権限を優先する場合の代替候補として維持した。
- ユーザー判断により、ガントを主遷移先から TODO の副次ビューへ降格し、Leantime TODO を主遷移先とする方針へ更新した。
- TODO の見た目と日常利用を重視した比較候補を `docs/candi-ref/todo-ui-candidates-2026-07.md` に整理した。Leantimeを実運用の本線、Vikunjaを最有力の比較対象、Kan / PlaneをUI参照候補としている。
- Vikunja の公式 plugin / Webhook / API を調査し、backend pluginは実験的かつUI未対応であることを確認した。実行基盤の優先候補をVikunjaへ更新し、まず無改変自己ホストとAPI / Webhook連携を検証してからfork要否を判断する方針を `docs/candi-ref/vikunja-fork-plugin-assessment-2026-07.md` に記録した。
- 横断ダッシュボードを、上段の処理フロー、下段の入口別量・候補種類・優先確認/判断ログの3列構成へ変更した。左ナビ幅も194pxへ圧縮し、指定画像と同じ情報階層に合わせた。`apps/web/test/api.test.mjs` と `apps/web/check.ps1` を確認した。
