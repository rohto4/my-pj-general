# 完了記録

## 2026-07-14 P0受入チェックの再配信状態同期

- 2026-07-14に実施済みのHub / Tasks再配信と、Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4の維持を、P0受入HTML・ユーザー手順・実装タスクへ同期した。
- 受入HTMLのR06/R07を、古い「Linux未配信」の赤固定から、再配信後の最終見た目・操作感を利用者が判定する黄の未判定状態へ変更した。既存ブラウザに保存された旧既定コメント付きの赤状態だけは自動移行し、利用者が将来手入力した未達状態は保持する。将来の未配信bundleは、利用者が個別に「未達」として赤へ戻す定常運用を維持する。
- `apps/web/test/api.test.mjs`に、配信済み事実が表示され、R06/R07をJavaScriptで赤固定しないことを検証する回帰を追加した。実データ変更、再配信、画像の追加取得は行っていない。
- 旧称「P0追加」の複数Project連携は、`p1-start-gate-acceptance-contract-2026-07.md`に合わせてP1開始候補へ再分類した。旧ファイル名は既存リンク互換のため維持し、P0の受入進捗からは除外する。
- P0の非破壊導線監査として、現行LinuxのHubとTasks主要9画面を読取り確認した。全画面でロード残留・document-level横overflowはなく、候補・task・設定は変更していない。Chrome consoleには2026-07-13のtoken renewal errorが2件残存していたため、今回の到達確認をconsole error 0の証跡としては扱わない。
- これはPJ固有の受入状態同期であり、横断ナレッジへの反映は不要と判断した。

## 2026-07-13 コンテキスト圧迫要因の実測と調査skill

- 作業前の保全として`d9b56eafb5ae8da5638f40cebe27bc433c67cd88`を`rohto4/origin/main`へpush済みであることを確認してから調査した。session JSONLは本文・画像・認証情報を表示せず、構造・件数・サイズ・tokenメタデータだけをストリーミング集計した。
- 初期読込751行・約44KB・約13,472 token（256Kの約5.3%）は主因ではなかった。一方で19回の圧縮直前は、観測可能な18回で実入力が各model windowの87.1〜94.0%に達していた。圧縮置換履歴には最終時点で`input_image`が30個、構造サイズ17.19MiBで残り、画像・添付・巨大tool出力が後続入力を早く再圧迫する実測を得た。
- `docs/imp/context-pressure-investigation-2026-07-13.md`へ確認方法、数値、限界、結論を残し、`docs/guide/context-pressure-session-guideline.md`を採用済みの閾値・セッション切替手順の正本として追加した。通常初期読込へは追加せず、診断または切替時だけ参照する。
- PJ skill `.agents/skills/audit-context-pressure/`を追加した。実装先行、設計書先行、混在、画像/ログ中心の4パターンを分け、セッションJSONLがある場合は内容非表示の構造集計、ない場合は推測と明示した作業packet監査へ分岐する。Node構文検査、実sessionのparse error 0・圧縮19回・最終画像30件の再集計、skill quick validatorを成功させた。
- knowledge-vault反映要否を評価した。既存の`G:\knowledge-vault\knowledge\dev\codex-auto-compact-recovery-design.md`は圧縮後の復帰設計を正本としており、今回のPJ固有実測の全文複写は不要と判断した。横断利用はPJ skillと本ガイドの参照で提供し、外部vaultの既存正本を重複更新していない。

## 2026-07-13 設計書化カバレッジ・役割別読込境界

- `docs/imp/design-documentation-coverage-assessment-2026-07-13.html`を、P0/P1完成度星取表とは別の5段階・クリック編集可能な設計書カバレッジ正本として追加した。入口取込、Hub候補・判断、Hub UI、Hub↔Vikunja、Tasks UI、再配信、LLM、複数Project、P1認証/PostgreSQL、継続同期の10機能について、正本・証跡・最小実装読込境界を対応付けた。
- P0/P1星取表の「設計書化カバレッジ / 役割別読込境界」は全10軸5/5・要確認なしへ更新した。旧ソース評価だけをこの更新時に初期化するため、他行のブラウザ内クリック評価は保持する。
- 不足していたHub UI操作契約、Tasks UI契約、複数Projectの体験・データ・連携契約・構成を、`docs/product` / `docs/spec` / `docs/data` / `docs/arch`の責務へ分離して補完した。実装済みかどうかと文書化の完成度を混同せず、P0実機受入の未達は従来のP0/P1星取表・受入HTMLで別管理する。
- `docs/guide/implementation-context-reading-guide.md`を追加し、圧縮・handoff後は役割別の最小正本文書を先に読み、必要時だけ対象実装へ進むルールを`AGENTS.md`へ同期した。
- PJ専用skill `audit-design-documentation-coverage`、`document-implementation-contracts`、`maintain-design-documentation`を追加した。Node静的回帰8件と`git diff --check`で検証する。skill-creatorのPython quick validatorはPyYAML非同梱のため実行できず、依存追加は行わない。
- 横断再利用できる原則のみを`G:\knowledge-vault\knowledge\dev\design-documentation-coverage-and-minimal-context-reading.md`へ転記した。PJ固有の受入状態・実装詳細・未完TODOはPJ内正本に残している。
- 実データ変更、Linux配信、再インポート、secretの参照・保存は行っていない。

## 2026-07-13 RV01〜RV04 Vikunja再受入のsource実装

- DashboardはPROJECT OVERVIEW guideとVIEWSを外し、Project名を薄い補助表記にした「<PJ名>のタスク概要」、左寄せの処理状況、完了taskを除いた`日付未定タスク`へ再構成した。
- Ganttは既定範囲を前14日〜向こう62日、日付ドラッグ/resize時の確認ダイアログ、キャンセル時にAPI更新を送らない境界、完了barを`0.28` opacityへ変更した。
- Kanbanはguideと固定縦高/内部縦scrollを外し、4列を維持したまま列内のtaskを全表示する。Task detailはbreadcrumbをtitle前へ移し、1438px相当でも右側に18remのsticky操作面を残し、説明・コメントの文字を0.82remにした。
- fork unitは51 files / 1090 testsが成功した。Linux custom image再build、1438x715 before/after JPEG、実画面受入は未完了であり、実データ更新は行っていない。

## 2026-07-13 Thread Line縮小版PNGのsource統合

- ユーザー提供の正式縮小アセット`docs/product/thread-line-logo-handoff-2026-07-12/assets/thread-line-mark-master-256.png`を、Hub `apps/web/assets/`とVikunja fork `frontend/src/assets/`へ配信対象として配置した。原寸`thread-line-mark-master.png`は制作・保管用のままとし、サイトへは含めない。
- HubとTasksの左レールはともに44pxの直角フレーム、1px輪郭、6px藍色オフセット、`object-fit: cover`で同一のTLマークを表示する。Hub輪郭は銅、Tasks輪郭はTasks青である。
- Hub Node 31件、Vikunja fork unit 51 files / 1090 tests、production buildが成功した。Linuxへのbundle更新・再build・実画面受入は未実施であり、実データ変更・再インポートは行っていない。

## 2026-07-12 P0フロント受入: R03実機完了

- ユーザーが現行Hub bundleをhash確認後にLinuxへ展開し、`pj-general` serviceだけを再build・再作成した。
- `/api/bootstrap` 200、管理画面の状態ラベル位置、取込／有効化／無効化の縦並び、管理カード2列配置、4K縦3分割相当の横崩れなしをChromeで確認した。
- Vikunjaの再作成、DB/files/volume削除、再インポートは実施していない。

## 2026-07-12 P0フロント実装断面: U03確認境界

- HubのGO／不要／アーカイブと保存してGOについて、送信前に「実データと判断ログを変更する」確認ダイアログを表示する境界を実装した。
- Node回帰28件、Python回帰7件、Hub/VikunjaのNode構文、星取表・受入HTML script構文、`git diff --check`を通過した。
- 更新Hub bundle `tmp/pj-general-web-working-tree.tgz`を作成し、SHA-256 `B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9`をR03手順・runbook・handoffへ同期した。
- 残りはThread Line PNG実装、U03/U04/U05の実画面受入であり、実データ変更・再インポートは行っていない。

## 2026-07-12 P0正式完了・P1計画

- P0の必須導線を、Hub回帰17件と既存Linux実機E2E証跡で再監査し、正式完了と判定した。
- P0正本から未実装のMisskey / Calendar / IdeaCard、自動AI整理を必須扱いする古い記述を除き、実装済み入口・Vikunja実行・状態mirrorへ同期した。
- Listening Lounge本流とVikunja frontend fork最終commit `325bc5475`、14状態の実データUI監査を完了証跡へ反映した。
- `docs/ops/p0-operations-runbook-2026-07.md` に起動、backup、restore、縮退、fork rollbackを整理した。
- 現在の実DB量と運用実績を基準にP1を再設計し、常設運用・観測、fork配信、定期入口workerを最優先にした。
- Misskey、重複束ね、部分自動確定、Calendar、PostgreSQL、認証を採用・PoC・条件付き保留へ分類し、P1ブリーフと実装タスクを作成した。

## 2026-07-12 P1-A ローカルhealth・backup

- `GET /api/health` を追加し、SQLite quick_check・件数とVikunja / local LLMの依存状態をsecret・URL・DB pathなしで確認できるようにした。
- 未設定・無効を正常縮退、設定不足・到達不能を `degraded` として区別した。
- SQLite online backup commandとPowerShell wrapperを追加し、timestamp世代、生成後quick_check、SHA-256、件数証跡を返すようにした。
- 実DBから候補19件のbackupを作成し、integrity `ok`を確認した。
- Node 17件、Python 3件、checkを通過した。coverage commandはchild process sourceを列挙しないためcoverage証拠から除外した。

## 2026-07-12 AI相談UX再設計

- 1280 x 720の実画面監査で、短文会話が細い縦箱へ潰れる、接続statusが暗く読めない、composerが初期表示外へ落ちる問題を特定した。
- 独立相談画面を、横一列のlive context、全幅会話、常時到達できるcomposerへ再構成した。後続の短高対応で説明用の大見出しと3段階フローを除去した。
- 空会話へ役割説明と入力スターターを追加し、Ollama / Gemma4の実接続情報を画面へ表示した。
- Windows版Ollama上の `gemma4:latest` へ実推論し、応答 `OK` と全ロード量のVRAM配置を確認した。
- UI契約テストを追加し、`apps/web/check.ps1` を通過した。
- 左サイドメニューへ常設のサイド相談ボタンを追加し、620px幅のdrawerが開くことを実操作で確認した。
- 会話数・thread・接続状態を1行化し、入力と送信を同じ行へ配置した。`max-height: 900px` / `650px` でAI相談内だけ文字と余白を縮小する。
- 1280 x 720でdocument overflowなし、live context 26px、message領域533px、入力・送信各52pxの完全表示を確認した。Node回帰18件、check、diff checkが成功した。

## 2026-07-11

- Windows 11ミニPCをUbuntu Server上のVikunja / pj-general実行環境へ移行するための、USB作成、OS導入、SSH、Firewall、Docker Compose、永続化、Secret保管、完了確認手順を docs/guide/linux-server-setup-for-vikunja.md に整理した
- Vikunja安定版とmainのAPI差分、状態分離、Webhook冪等性、Secret境界をレビューし、実機受入試験とCompose/env雛形を追加した
- Vikunja `v2.3.0`とpj-generalをLinux上で実データ結合し、GO、二重作成防止、署名Webhook、再照合、再起動、backup/restoreを実機確認して仮完了とした

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
# 2026-07-10 Vikunja結合設計・実行環境確認

- Vikunja upstreamを`G:\devwork\clone-dir\vikunja-upstream`へcloneし、`rohto4/vikunja` GitHub forkを作成した。
- cloneは`upstream`と`origin`を分離し、初期fork差分を持たない追随起点にした。
- `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md` にコンポーネント図、データフロー図、責務境界、fork/plugin判断基準を作成した。
- `docs/data/vikunja-integration-data-design-2026-07.md` にexecution link、Webhook event、再試行、冪等性、PostgreSQL移行を含むデータ設計を作成した。
- `docs/arch/vikunja-linux-deployment-and-operations-2026-07.md` にLinux常設配置、秘密情報、TLS、バックアップ、更新・復旧手順を作成した。
- `docs/spec/vikunja-integration-contract-2026-07.md` にGO登録、Webhook受信、再照合の論理契約を作成した。upstreamソースからAPI v2 task route、`event_name` / `data.task` payload、`X-Vikunja-Signature`を確認した。
- 同契約へGO登録とWebhook反映のシーケンス図を追加し、実装時の責務と失敗時の状態を明確化した。
- 既存比較資料のWebhook再試行に関する断定を、upstream source E2Eとrelease差分を考慮した冪等保存・定期照合前提へ修正した。
- Windows側にGo・Docker・WSLがなくVikunja本体を実データで起動できないため、モックAPI接続は作らず、Linux実行環境準備を実機結合の開始ゲートにした。
- 横断的な設計原則を`G:\knowledge-vault\knowledge\dev\self-built-intake-and-layered-pm-oss-selection.md`へ、公式仕様のsource noteを`G:\knowledge-vault\sources\vikunja\vikunja-plugin-webhook-api-2026-07.md`へ反映した。
- 設計チェックポイントを`eb172e3`、upstream仕様差分の修正を`5ba24c5`としてGitHubへpushした。

# 2026-07-11 Hub / Tasks導線結合

- `GET /api/integrations/vikunja/overview` を追加し、Vikunja API v1のproject概要と直近タスクをHubへ表示できるようにした。
- HubダッシュボードにTasks側の全件数・未完了・完了、直近タスク、Tasks側プロジェクトへのリンクを追加した。
- 確認待ち詳細、書き入れ口の作成後プレビュー、参考ガントからTasks側へ遷移できる導線を整理した。
- GO後はTasks側でタスク実行を完結し、Hubは入口・候補・判断・連携状態を保持する一方向境界を設計書へ反映した。
- 概要APIはtokenを返さず、未接続・接続失敗を画面で扱い、既存GO/Webhook/再照合と結合するテストを追加した。
- `apps/web/test/api.test.mjs` 10件、Python 3件を通過し、Linux実機の概要APIと配信ファイルを確認した。

# 2026-07-11 Hub / Vikunja UI調和

- Vikunja `v2.3.0`の配信CSSを確認し、青 `#126cfd`、白・薄いグレー、黒寄りの文字、明確な境界線をHubの視覚基盤へ反映した。
- Hubの色トークン、パネル、表、詳細ブロック、フォーム、無効状態、選択状態、Tasks側リンクを2段階で調整した。
- 装飾的なグラデーション、大きなピル形状、過剰な角丸を減らし、業務ツールとしてのソリッドな見た目へ寄せた。
- 実画面でダッシュボードのTasks概要、直近タスク、QueueのTasks側リンク、Tasks側URLを確認した。
- Vikunja upstream本体は変更せず、Hub側の視覚と導線を寄せる方針を維持した。次はユーザーの微調整を受ける段階とする。

# 2026-07-11 Cozy Rich Theme Lab 4案

- 現行プロダクト・クリエイティブサイト24件を調査し、参考URLと抽出原則を `docs/candi-ref/modern-rich-cozy-ui-references-2026-07.md` に記録した。
- PJ用skill `design-cozy-workspace-ui` を作成し、角丸予算、狭幅再構成、実データ維持、スクリーンショット監査を固定した。
- 旧2案を破棄し、`theme-room-01` から `theme-room-04` の4案へ置き換えた。
- 本流のDOM、操作コード、SQLite、APIを共有し、テーマ専用データやモックを作らない境界を維持した。
- 添付相当の1265px幅と1920px幅で、横overflow 0、入口別と候補種類の下端差0px、2px超の構造角丸0件を確認した。
- 書き入れdrawer、AI相談drawer、確認待ち種類filterを実ブラウザで確認した。
- Node 12件、Python 3件を通過した。

# 2026-07-11 ローカルLLM相談窓口 v1

- Hub SQLiteへ `chat_threads`、`chat_messages`、`chat_task_suggestions` を追加し、会話履歴をprovider側へ依存せず保存するようにした。
- OpenAI互換 `POST /v1/chat/completions` adapterを追加し、Ollama `gemma4:latest`、llama.cpp等を環境変数で切替可能にした。Ollamaの思考モデルは既定で `think: false` とし、回答本文が空になる挙動を回避した。
- Hub候補と実行状態、Vikunja project概要・直近taskを毎回contextとして渡す。tokenやsecretはcontext、履歴、公開レスポンスへ含めない。
- 構造化 `THREADLINE_TASK_PROPOSALS` をparseし、ユーザーのボタン操作後だけ既存 `candidates.status=pending` へ追加する。直接GOやVikunja task作成は行わない。
- `/chat` 独立画面と、通常画面から開くサイドウィンドウを追加し、同じthreadと候補操作を共有した。
- 固定応答統合テスト、Ollama実endpoint、`apps/web/check.ps1`、Node 12件、Python 3件を確認した。

# 2026-07-12 ローカルLLMエージェント相談窓口の要件統合

- 既存の `/chat` 独立画面、Hubサイドウィンドウ、SQLite会話履歴、候補pending化を今回の「相談から直でタスク候補化する窓口」の実装正本として整理した。
- `get_threadline_context` の読み取り専用toolに `all` / `tasks` / `candidates` scopeを反映し、agentが必要なThreadline情報だけを取得できるようにした。
- タスク作成・GOはLLMへ許可せず、画面のユーザー操作から既存確認待ちキューへ送る境界を維持した。
- tool callingの2段階応答、Tasks scopeの返却範囲、回答継続を統合テストで確認した。

# 2026-07-12 固定Ganttサンプルの除去

- `apps/web/db_tool.py` の固定 `GANTT_TASKS` を削除し、SQLite候補の予定日とVikunja実行状態の期限からTasks連携予定表示を生成するようにした。
- 日付を持たない候補はGanttへ表示せず、現在週起点の4週目盛りと空状態を表示する。固定日付・固定タスク名によるモック表示は残さない。
- API回帰テストで、初期Ganttが空であること、日付付きSQLite候補追加後だけ行が現れることを確認した。

# 2026-07-12 Listening Lounge 本流昇格

- 4案比較からユーザーが選定した `Listening Lounge` を、通常URL `/` の恒久テーマへ昇格した。
- `room-base.css` とテーマ3の意匠を `apps/web/listening-lounge.css` に統合し、本流HTMLから直接読む構成へ変更した。
- 一時テーマ切替と4案routeを本流配信から外し、旧 `/theme-room-03` は `/` へリダイレクトした。
- 本流DOM、SQLite、API、書き入れ、AI相談を維持し、テーマ専用データやモックを追加していない。
- 1280x1400と1920x1080で、横overflow 0、入口別と候補種類の下端差0px、2px超の構造角丸0件を確認した。

# 2026-07-12 Linux配信bundle準備

- Linux側の旧配信をHTTPで確認した。Hub `/api/health` は404で、HTMLにもListening Lounge / AI相談の現行マーカーがなく、再起動だけでは刷新内容が反映されない状態だった。
- Hub `apps/web` とVikunja Listening Lounge forkの現行working treeを、永続データ・依存物を除いた転送bundleへ固めた。
- Vikunja sidebar identity headerの契約テストを修正し、Vikunja対象テスト12件を通過した。
- 再build・実機受入は、Codex環境からLinux SSH公開鍵認証が通らないため未完了。正本手順は `docs/guide/linux-listening-lounge-deploy.md`。

# 2026-07-12 P1-A source observability

- `source_sync_runs` をSQLiteへ追加し、knowledge-vault / Slack importの開始・完了・cursor・scanned / created / skipped / failedを記録するようにした。
- Vikunja reconcileも同じrun契約で記録し、`GET /api/observability` からsource別の直近結果とHub backup世代のintegrity / SHA-256 / 件数を取得できるようにした。
- 管理画面へ運用観測パネルを追加し、source同期、reconcile、backupの直近結果を画面で確認できるようにした。
- Node回帰20件、Python 3件、`apps/web/check.ps1` を通過した。Linux実機でのtimer、外部媒体複製、Vikunja restore drillは未完了。

# 2026-07-12 P1-C sync oneshot

- `workers/sync/run.py` を追加し、knowledge-vaultとSlack payloadを同じSQLite同期契約で単発実行できるようにした。
- `source_sync_runs` のcursor before/after、created / skipped / failedを使い、同じ入力の連続2回を冪等に処理する。
- lock fileの排他、source単位の失敗分離、systemd `Type=oneshot` / 6時間timer / `Persistent=true` の雛形を `infra/systemd/` に追加した。
- worker unittest 4件を通過。Linux上でのsystemd実行、Slack connectorからのpayload生成、常設secret配置は未実機確認。

# 2026-07-12 P1-A backup rotation

- `infra/backup/rotate-and-mirror.sh` を追加し、Hub / Vikunja DB、Vikunja files、secret設定を世代単位で退避し、`manifest.sha256`を生成するようにした。
- `KEEP_GENERATIONS`による世代保持と、`MIRROR_ROOT`を指定した場合だけ外部媒体へ複製するsystemd daily timerを追加した。
- backup policy unittest 2件を通過。Linux実機での初回backup、外部媒体、restore-testは未完了。

# 2026-07-12 P1-B release scripts

- `infra/vikunja/build-listening-lounge.sh` でrelease versionとcustom image tagを固定し、`switch-image.sh` でstable/customをデータvolume非変更のまま切り替えられるようにした。
- stable rollbackは `vikunja/vikunja:2.3.0` のimage参照へ戻すだけの契約とし、スクリプトテスト2件を通過した。
- Docker build・Linux起動・実データrollbackはSSH認証待ちのため未実機確認。

# 2026-07-12 P1運用metrics

- `/api/observability` に候補総数・確認待ち・不足項目、入口別・種類別・信頼度別、判断・GO・Tasks完了の集計を追加した。
- 管理画面の運用観測パネルへ候補 / 確認待ち / GO / Tasks完了 / 不足ありの5指標を追加した。
- Node回帰20件で、同期・backup証跡とmetricsの実データ応答を確認した。

# 2026-07-12 P1-A reconcile timer

- `workers/reconcile/run.py` と `pj-general-reconcile.timer` を追加し、Hub復旧後に15分間隔でVikunjaの実行状態を再照合できるようにした。
- 接続不能時は終了コード1とJSONの`unavailable`を返し、systemd journalへ残す。Linux実機でのHub停止→復旧連続確認は未完了。

# 2026-07-12 P1 PoC readiness

- 現行実DBの19候補（全件pending、decision 0、execution link 0、missing 19）を観測し、Misskey / 類似 / 部分自動確定 / Calendar / PostgreSQL / Auth PoCを暫定保留として整理した。
- 最終判定ではなく、GO・不要・完了・source runの実運用データを収集してから採用 / 保留 / 対象外へ昇格する入口を `docs/imp/p1-poc-readiness-2026-07-12.md` に固定した。
- `workers/poc/dry_run.py` を追加し、現行19候補から類似4組を提示、部分自動確定はeligible 0 / blocked 19を確認した。いずれもDB変更と自動GOは行っていない。

# 2026-07-12 P1 restore drill

- `infra/vikunja/backup-and-verify.py` がHub / Vikunja DBを別restore-testへ復元し、integrity、対象件数、`execution_links`件数、backup/restore SHA-256を出力するようにした。
- fixture DBによるrestore drill test 1件を通過。Linux実DB、files、secret設定を含む実機restoreはSSH認証後に実施する。

# 2026-07-12 P1 verification matrix

- P1要件をローカル証跡とLinux実機証跡へ分離した検証マトリクスを `docs/imp/p1-verification-matrix-2026-07-12.md` に追加した。

# 2026-07-12 P1 PoC契約整理

- `workers/poc/calendar_dry_run.py` とテストを追加し、現行実DBでCalendar一方向eventを外部書き込みなしでdry-runした（approved 0件、`wouldCreate=0`、`externalCalls=0`）。
- Better Auth導入前の resource-action matrix を `docs/spec/auth-resource-action-matrix-p1.md` に整理した。GO、外部task作成、restore、secret参照は明示確認またはownerに限定する。
- PostgreSQL移行の対象、件数・hash・外部ID比較、rollback境界を `docs/spec/postgresql-migration-dry-run-contract-p1.md` に固定した。実DBdry-runは導入ゲート後まで保留する。

# 2026-07-12 P1 Vikunja guide / release procedure

- VikunjaのHome、Dashboard、Inbox、List、Table、Kanban、Gantt、Task detailを、役割・入力・結果・次操作のinventoryとして `tmp/ui-review/vikunja-listening-lounge/README.md` に固定した。
- 共通`WorkspaceGuide` / `WorkspaceEmpty`とview別guide、折りたたみ状態、0件状態をfrontend forkへ反映し、対象unit 24件・stylelint・production buildを通過した。
- `docs/guide/linux-listening-lounge-deploy.md` にstable `v2.3.0`を基準にしたupstream fetch / range-diff / rebase / 回帰 / custom build / rollback手順を追加した。Linux実機実行はSSH認証後に行う。

# 2026-07-12 P1 source sync domain separation

- `apps/web/source_sync.py`へknowledge-vault / Slack import domainを分離し、HTTP境界の`db_tool`互換wrapperと`workers/sync`が同じ実装を共有するようにした。
- source sync domain 2件とworker 4件の回帰を通過し、Web handler経由とoneshot worker経由の同期run契約が同じであることを確認した。

# 2026-07-12 P1配信bundle再生成

- `apps/web/source_sync.py`とCalendar PoCを含めるためHub / P1 bundleを再生成した。
- 最新SHA-256はHub `9AE0C741D645EE1F3CEE3EBC88B8C079DD63A72DC038C6302592C211F2F65EE0`、P1 `6A73873F8D6119F61AC170B0BB3AF5BDAC13B7BD9C5F7BBB8F1B39B880659CD5`。配信手順のmanifestも更新した。

# 2026-07-12 P1完了監査

- P1の完了条件を`docs/imp/p1-completion-audit-2026-07-12.md`へ整理し、ローカル証明済み・設計済み・Linux/実運用待ちを分離した。
- 直前時点ではSSH公開鍵認証待ちだったため、Linux再配信・timer・restore・rollbackを保留していた（後続のLinux実機更新で再配信とrestoreを実施）。

# 2026-07-12 Linux実機再配信・再起動

- SSH公開鍵登録後、Linux `universe`へ接続し、Hub/P1/Vikunja bundleのSHA-256一致を確認した。
- 再起動前に実DB backup/restore drillを実行し、Hub candidates 19、execution links 2、Vikunja tasks 2、backup/restore hash一致を取得した。
- 最新Hub bundleから`pj-general/web:p0`を再build・再作成し、Vikunja stable `v2.3.0`とともに再起動した。再起動後も19候補、2 link、2 taskを保持し、再インポートは行わなかった。
- Hub `/api/health`はDB/Vikunja `ok`、Ollama未接続で`degraded`。`/api/observability`へ実DBHub backup世代を表示できるよう`P0_BACKUP_DIR`を設定した。
- custom Vikunja image build、systemd `/etc`登録、外部mirror、Hub停止→reconcileはsudoパスワード入力待ちで残っている。

# 2026-07-12 P0フロント受入 セッション2・静的監査

- `docs/imp/p0-frontend-operation-audit-2026-07-12.md`に、Hub / Vikunja主要画面のbutton・link・form、API対応、無効・読み取り専用・empty状態を集約した。
- Hub UIへ、候補・判断・GOはHub、title・期限・担当・進捗・完了はTasks側という編集責務、Tasks状態mirror、未接続/接続失敗時の次操作を追加した。
- `Tasks概要`ナビはHub内anchorに固定し、Tasks外部リンクと混同しないようにした。Node 21件、Python 5件、構文チェックを通過した。
- 4199番の現行ソースは`/api/bootstrap` 200を確認した。一方、アプリ内ブラウザからは4199番へ到達できず、4173番は現行`/api/bootstrap`を返さない旧プロセスだった。実データへ変更・再インポートは行っていない。
- 旧テーマ比較タスクと旧Hub/Vikunja調和タスクは、Listening Lounge本流とP0フロント受入の正本へ統合済みのため削除した。

# 2026-07-12 Linux Hub recovery helper

- `infra/vikunja/recover-pj-general.sh` を追加した。HubコンテナのCompose labelから実Compose定義・serviceを自動特定し、`--status`、`--redeploy-hub`、`--restart-all`、`--dry-run`の分岐で安全に復旧できる。
- volume削除、Compose project全体の停止、データ再インポート、env内容の出力は行わない。Hub bundle展開前に`apps/web/Dockerfile`を検査し、想定外deploy rootへの展開を止める。
- Pythonの安全ガードテストを追加して成功。Windows環境にはbash / WSL distroが無いため、bash構文実行はLinux実機で`--help`と`--dry-run`を先に確認する。
- Listening Lounge forkをVikunjaの既定復旧imageとして扱うよう、`--restart-all`は`rohto4/vikunja:2.3.0-pj-general-listening-lounge`を明示して再作成する。別imageを使う場合だけ`--vikunja-image`を指定する。

# 2026-07-12 統一起動構成の準備

- `infra/deploy/compose.yaml`へHubとListening Lounge版Vikunjaを統合し、既定imageを`rohto4/vikunja:2.3.0-pj-general-listening-lounge`に固定した。
- `infra/deploy/start-pj-general.sh`は、fork bundleからのsource展開・custom image build・Hub/Vikunja一式起動・health確認を1入口にまとめた。`--dry-run` / `--status`も備え、volume削除・再インポートはしない。
- Linux実機へは未配置・未実行。次回は現行データを保ったまま、統一deploy rootへ配置してdry-runから開始する。

# 2026-07-12 統一起動の初回コンテナ引継ぎガード

- Linuxで統一起動scriptの初回`--dry-run`を確認した。custom Listening Lounge imageは存在済みで、Hub/Vikunjaの一式起動コマンドだけが表示された。
- `infra/deploy/start-pj-general.sh`へ`--adopt-existing`を追加し、旧split Composeが所有する同名`pj-general` / `vikunja`コンテナを通常実行で誤って置き換えないようにした。
- 明示指定時だけ旧コンテナを削除して統一Composeのコンテナへ置換する。volume、bind mountのDB/files、image、再インポートを操作しない。Linuxで更新scriptのdry-runと実行を確認するまで、P0フロント実画面受入はブロック状態を維持する。

# 2026-07-12 P0受入チェックHTML

- P0 / P0追加の残確認を`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`へ集約した。Listening Loungeの星取表テーマを継承し、Linux/配信のブロックを赤、見た目・操作感・実データ変更を伴う受入を黄として上から実行できるようにした。
- 各項目は完了／未達の排他的チェック、未達理由・画面幅・task IDを残すコメント欄、Codexへ貼る報告プロンプトの生成・コピーを備える。入力はブラウザのlocalStorageだけに保存し、secretや実データをHTMLへ出力しない。
- 星取表のP0 / P0追加は、実証済みまたは手順が固定された黄／赤セルとして5段階表現を統一した。ガント担当者のobject表示修正はR01としてLinux再配信待ちである。
- ワークスペース付属runtimeで、Hub Node回帰24件、Hub Python回帰7件、統一起動Python回帰2件を実行し成功した。従来PATHにNode/Pythonがないことはテスト未実行の理由にせず、付属runtimeを明示して実行する。
- 受入HTMLのA01（実機基盤）とA02（回帰・Hub画面幅）は初期状態で完了チェック済みとした。過去の星クリック値が新しいP0/P0追加の5/5基準を上書きしないよう、星取表のlocalStorage keyをv2へ更新した。
- `app.js`と`server.mjs`のNode構文検査、および`git diff --check`を実行し、エラーなしを確認した。PowerShell実行ポリシーにより検証wrapperの直接実行はできないが、同じNode構文検査と個別回帰は付属runtimeで実施済みである。
- P0受入フィードバックに基づき、HubのGanttは初回描画・visibilitychange・resize後に再layoutし、判断ログはDBの最新順を再取得するよう修正した。候補の表示名、判断ログ、Gantt、Vikunja作成task名はTODO案を優先する。Node 25件、Python 9件で回帰成功し、R02の再配信待ちである。

## 2026-07-12 knowledge-vault 転記

- 転記先: `G:\knowledge-vault\knowledge\dev\self-built-intake-and-layered-pm-oss-selection.md`
- 日時: 2026-07-12 19:05:49 +09:00
- 対象: 同期run観測と冪等worker、secret非露出のhealth / observability、backup / restore検証、stable/custom imageの安全なrollback、dry-run中心の復旧ガード。

# 2026-07-12 Thread Line TLロゴ選定・SVG仕様化

- ユーザーが銀白ホワイトグラスの中光沢案を最終選定し、`assets/07-silver-white-glass-selected.png`へ視覚基準として保存した。
- 生成画像を直接配信せず、`VECTOR-SPEC.md`へ1000単位のpath、orbit太さ、色、四芒星位置、master / Hub / Tasks配色差を固定した。
- `NEXT-SESSION-PROMPT.md`を画像探索用からSVG実装用へ更新した。次回はSVG単体previewを先に承認し、Hub / Tasks実装、Linux配信、Docker、実データ操作を別断面として扱う。
- 今回はPJ固有のブランド選定と実装待ち整理であり、横断ナレッジへの転記対象なしと判断した。

# 2026-07-12 Thread Line master SVG出力

- 最終視覚基準をT/Lの低光沢サテン立体感と穏やかなgradientを持つ`08-satin-gradient-selected.png`へ更新した。
- `thread-line-mark-master.svg`を透明背景、bitmap埋め込みなし、1000単位の決定論的pathとして出力した。
- XML parse、透明背景、bitmap未埋め込み、Chrome headlessによるlight/dark背景描画を確認した。Hub / Tasks文脈配色とアプリ組み込みは後続タスクに残した。

# 2026-07-12 Thread Line SVG方針撤回・PNG確定

- SVG再構成で字形、orbit曲率・太さ、光沢が原画像から大きく劣化したため、SVG候補を不採用として削除した。
- `08-satin-gradient-selected.png`と同一内容の`thread-line-mark-master.png`（1254px）と、高品質bicubic縮小の`thread-line-mark-master-256.png`（256px）を正式アセット候補として出力した。
- 今後は画像の描き直しやSVG化を行わず、PNGをそのまま実装して実表示サイズで確認する。

# 2026-07-12 P0完成度レビュー証跡

- 既存のVikunja実機受入JPEGを元に、RV01〜RV05の黄色枠付きレビュー画像を`tmp/ui-review/p0-review-2026-07-12/`へ保存した。
- Dashboard密度、Gantt空白/時間軸、Kanban 4列/内部スクロール、task detail読み順、before/after証跡の画面高不一致を、問題確定ではなくユーザー判断対象として切り出した。
- P0受入チェックHTMLの上部へレビュー項目を追加し、画像リンク・完了/未達チェック・コメント・報告プロンプト生成を接続した。実データ変更なし。

# 2026-07-12 P0受入JPEGギャラリー

- `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`の再受入JPEG一覧を、before/afterのサムネイル18枚をHTML内に表示するギャラリーへ拡張した。
- サムネイルクリックで拡大表示し、閉じるボタン・背景クリック・Escキーで戻れる。画像の元ファイル、実データ、localStorageの受入結果は変更していない。
- `apps/web/test/p0-checklist-gallery.test.mjs`を追加し、ギャラリー・拡大表示用のDOMと代表JPEGリンクを回帰検証した。

# 2026-07-12 U03判断ログ再描画ガード

- `refreshBootstrap`をbootstrap取得とobservability取得へ分離し、observability APIだけが失敗しても候補・判断ログを反映するようにした。
- `apps/web/test/api.test.mjs`へ、refreshBootstrapの分離・fallbackを確認する回帰を追加した。実データ操作は行っていない。

# 2026-07-12 Tasks左レールのアイコン配色

- Vikunja forkの左レールでHubと同じUnicode記号・輪郭・24px幅・行高を使い、Hubは銅オレンジ、Tasksは`--threadline-tasks-accent`の青で表示するテーマ修正を追加した。
- `threadline-listening-lounge.test.ts`へ配色・記号の回帰を追加し、forkの対象テスト13件が成功した。Linux配信とユーザー実機確認は未完了。

# 2026-07-13 P0再配信・受入チェック断面

- P0受入HTMLへ赤ブロッカーR04を追加し、Thread Line共通44px識別とRV01〜RV04の最新sourceを一つのLinux再配信手順へ集約した。過去のR02/R03/V01は履歴の完了として保持し、今回の実行対象と混同しない。
- Hub bundleはSQLite・テストを除く実行対象だけへ再生成し、SHA-256を`E913041297C18D257BEEE560F239CB3AE828D8C06F40C7E45F96CAA3152E693A`へ更新した。Tasks bundleは不要な`frontend/dist-guide-test`を除外して再生成し、`BC0C8B8B7462FA5524C973B690AFC0C083DD34B7A55C54E55B5D227993D64C7A`へ更新した。
- R04はHub `/api/bootstrap` 200とVikunja `/api/v1/info` 200を待機後に確認する。DB/files/volumeの削除、env表示、再インポートは手順に含めない。
- Hub受入チェック回帰31件（Node test runner）と`git diff --check`を実行し、テストは成功、空白エラーはなしを確認した。Linux実行と実データ変更は行っていない。

# 2026-07-13 星取表の実態再評価

- P0 / P0追加のHTML星取表で、P0本体にも未受入のUI/UX・連携・安全を残すよう評価を下げ、黄色の要確認セルを追加した。契約・SQLite・回帰の達成を、未確認の画面品質や実機運用の満点根拠として扱わない。
- `現在の作業`をR04のLinux再配信待ちに同期し、Thread Line・RV01〜RV04の赤ブロッカー、RV01〜RV05/U01〜U03/U05の黄受入を明示した。ユーザーがクリックした星のローカル保存とHTML内の編集機能は維持する。
- Node回帰31件と`git diff --check`を再実行して成功した。実データ変更は行っていない。

# 2026-07-13 U02 新規候補の要約・タグ品質改善

- knowledge-vault / Slackの新規候補は、Markdown見出しを除いた本文を抜粋し、本文・入口・相対参照に基づく要約を作るようにした。固定の「取り込んだ確認候補」という文だけを要約に使わない。
- 既存の表示可能なタグマスタから、本文の`gantt` / `tasks` / `ui` / `schedule` / `review` / `research`等の語と一致するタグだけを追加選択する。入口の来歴タグは維持する。TODO案は候補タイトルを優先し、一覧・判断ログ・GO先の表示名と一致させる。
- AI相談のsystem promptにも、推測や定型文を含めない要約、具体的な行動句のTODO、タグを推測で増やさない指示を追加した。既存候補19件は再インポートせず変更していない。
- Node回帰31件、Python回帰8件が成功した。新規AI相談候補1件を作る実機品質受入は実データ変更のため、ユーザーの明示確認を待つ。

# 2026-07-13 R04前の公開画面確認

- 読み取り専用でChromeの公開Hub / Tasksを確認した。Hub左レールは旧`P0 / pj-general`表示のまま、Tasks左レールは旧`Vikunja / Tasks workspace`、Kanbanには旧`KANBAN VIEW` guideが残っている。
- よってR04の未配信は実画面で確認済みであり、Thread Line 256px識別・RV03のguide非表示を完了扱いにしない。候補、task、設定、ブラウザ内データは変更していない。

# 2026-07-13 U03 判断操作IDの照合実装

- Hubの編集・不要・アーカイブ・GO送信は操作IDを発行し、API応答の`decision.operationId`、`bootstrap.log[].operationId`、SQLite `decisions.note`の`operation:<ID>`を同一IDで照合できるようにした。判断ログ画面にも操作IDを表示する。
- テスト先行で編集・不要・アーカイブ・GOの各経路を追加し、HTTP応答と最新ログの一致を検証した。Hub Node回帰31件、Python回帰8件、`git diff --check`は成功した。実データ操作、再インポート、Linux Docker操作は実施していない。
- Hub実行bundleをSQLite・テスト・一時ディレクトリを除いて再生成し、SHA-256を`E8EBE20B4C7913437BF8C2FE9F83D7B5FD656C2DBC7257D6A95B138FE9B74AA7`へ更新した。R04はこのHub hashと既存Tasks hashを照合してから実行する。

## 2026-07-13 U03 ブラウザ上のHTTP証跡

- 判断後のHub通知にも`HTTP 200`と操作IDを表示し、受入者が開発者ツールを開かずにAPI成功・画面判断ログ・SQLiteを同じ操作IDで照合できるようにした。
- Hub bundleは`4AF5C14E7F180B2C31E9C9E4C119B7D315CE53DDA57C76AF226F3457FC5F3AC6`へ再更新した。R04はこのhashを正本とする。実データ変更、再インポート、Linux Docker操作はしていない。

## 2026-07-13 knowledge-vault 転記

- 転記先: `G:\knowledge-vault\knowledge\dev\self-built-intake-and-layered-pm-oss-selection.md`
- 日時: 2026-07-13 07:23:07 +09:00
- 対象: U02の本文根拠に基づく候補要約・既存タグ制約・来歴保持・再インポート回避、およびU03の操作IDをHTTP応答・画面ログ・SQLiteで一致させる追跡性。

## 2026-07-13 R04実機反映とR05左レール最終修正

- ユーザーがR04をLinuxへ再配信し、Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`を確認した。Hub実データはcandidates 19 / decisions 9 / execution links 4を維持し、再インポート、DB/files/volume削除は行っていない。
- 公開Kanbanのguideが残った実機差分を確認し、表示名`Kanban`への依存ではなく固定の`viewKind === 'kanban'`で抑止する修正をテスト先行で実装した。
- 左レールはHubを薄橙`Thread Line Hub`、Tasksを薄青`Thread Line Tasks`へ揃え、旧副題を除去し、Inbox等のProject行へTasks青の24pxアイコンを追加した。Hub Node 31件、Tasksテーマ17件、Tasks型検査が成功した。
- 最新bundleはHub `84A85F4398856176441C8490E5A73104844353C8A0BB7E17883A071626B286C8`、Tasks `9FCB7996DEABFBCAFA78DE8F4D81F7A48FF80A4852DA1884E41A8C5E8065E334`。次のR05は`infra/deploy/redeploy-p0-frontend.ps1`をWindows PowerShellで一行実行するだけとし、hash照合、source-only展開、再build、両API 200の確認をscript内へ集約した。
- 初版scriptはPowerShell/SSHのTTY経由でhash環境変数が空になり、展開前のhash照合で安全に停止した。R05 scriptはhashをremote shellの位置引数として渡すよう修正し、script回帰2件と`-DryRun`を再実行した。失敗時点でDB/files/volume、既存source、実データには触れていない。
- 位置引数を標準入力で渡す方式も、対象SSHでは対話shell扱いになったため展開前に安全停止した。R05 scriptはhelperを`/tmp`へ転送後、通常のSSH remote commandとして`bash /tmp/redeploy-p0-frontend-remote.sh <hub-hash> <tasks-hash>`を起動する方式へ再修正した。これによりsudoは割り当て済みTTYから通常どおり入力できる。
- remote command引数の伝達差異を完全に避けるため、Windows scriptがHub/TasksのSHA-256だけを書いた一時manifestを生成・転送し、remote helperは`/tmp/pj-general-p0-redeploy-hashes.txt`から期待hashを読む方式へ最終化した。manifestはsecretやenvを含まず、Windows側は実行終了時に削除する。

## 2026-07-13 R05再配信完了

- ユーザーが`infra/deploy/redeploy-p0-frontend.ps1`を一行実行し、Hub/Tasks bundleをhash照合後に安全に展開・再buildした。起動直後の接続失敗は待受中の一時状態であり、最終的にHub `/api/bootstrap=200`とTasks `/api/v1/info=200`を確認して成功した。
- 実データはSQLite integrity `ok`、candidates 19 / decisions 9 / execution links 4を維持した。DB/files/volume削除、再インポート、env/secret表示は行っていない。
- R05のLinux配信ブロッカーは解消した。残りはChromeで強制再読込後にThread Line左レールとKanban guide非表示を確認する黄色の実機受入である。

## 2026-07-13 R06 Tasks本文テーマの青・淡青統一

- R05後の実機確認で、Tasksの本文にHub由来のオレンジが残ることを確認した。TasksはHubと形状・情報密度を共有しつつ、本文のブランドアクセントはTasks青と淡青だけを使う要件へ固定した。
- fork themeのprimary/link/focus/選択行/left rail/button/card/task/dashboard/calendarおよびlogin装飾の銅オレンジをTasks青`#5176d8`／淡青`#89b8ff`へ置換した。テーマ回帰18件、stylelint、production buildが成功した。fork全体の`vue-tsc`は既存上流型不整合で失敗するが、本SCSS変更の新規型エラーではない。
- 更新Tasks bundle SHA-256は`B841C75C21D6D4B10BA262189B9533287C30E23A6D0C0E3FCA73A836359A57DE`。再配信は既存の一行`redeploy-p0-frontend.ps1`だけで行い、DB/files/volume削除・再インポートをしない。実機のオレンジ残存なし確認はR06へ残す。
- 続く実機レビューで、Tasksの薄青が識別リンク全体を塗っており、Hubのタイトル面だけを塗る骨格とずれることを確認した。Tasks識別面をマーク右のタイトル面だけへ変更し、更新bundle SHA-256を`4EB8CF69FDF03FE7586CCD95E94E80B36293CD2B612AD7B14373D184097CECCA`へ更新した。R06で同時に再配信・受入する。
- TasksのProject／Label／Teamを`マスタ管理`へ統合した。左レールは単一の`マスタ管理`入口とし、3セクションで登録・確認、既存の個別URLと作成／編集フォームは互換性のため維持した。テーマ回帰19件、stylelint、production buildを確認し、更新Tasks bundle SHA-256を`D166BBCBCC56414D00E4278C4710B91FC750054902CEAF9DA090D82DCF39B85D`へ更新した。Linux再配信と実機受入はR06/R07として残す。

## 2026-07-13 knowledge-vault 転記（R04/R05遠隔再配信ガード）

- 転記先: `G:\knowledge-vault\knowledge\dev\self-built-intake-and-layered-pm-oss-selection.md`
- 日時: 2026-07-13 13:25:18 +09:00
- 対象: R04/R05で確認した、bundle SHA-256の一時manifest伝達、hash一致前の展開禁止、TTY・標準入力・環境変数の伝達失敗時の安全停止、最終API 200確認、SQLite integrity・件数確認、削除・再インポート・secret表示を行わないsource-only再配信ガード。

## 2026-07-13 Hub左レール再編とP0受入定常ゲート

- Hub左レールを`ダッシュボード / 簡易日程 / タスクキュー / ワークビュー / 簡易管理`の5導線へ再編し、各項目のHub内スクロール先見出しも同名へ同期した。
- 通常メニューの相談は廃止し、AI相談と未実装・非活性の`詳細管理`を同じ下部ボタン群へ分離した。詳細管理は状態変更を起こさず「準備中」を示す。
- 上から実行するP0受入チェックでは、R06/R07を先頭の「定常作業 / 配信状態と実機反映」へ固定した。HubまたはTasksの配信資材を更新した回は同じ安全な再配信scriptで両方を反映し、Linux環境が最新版でなければ「未達」で赤に戻す。
- `redeploy-p0-frontend.ps1`は実行直前にHub / Tasksのsource-only bundleを現行sourceから再生成するよう変更した。古い`tmp/*.tgz`を誤って配信せず、以後は同script一行とSSH / sudoの対話パスワード入力だけで最新版を安全に反映できる。新Hub左レール資材のLinux反映前はR06/R07を赤のまま維持する。
- 左レールのハッシュ遷移は絶対パス付きリンクと手計算offsetを廃止し、同一ページの相対hashと共有scroll処理へ統一した。Dashboard / Gantt / Queue / Worker / Adminの各セクションは同じscroll marginで見出し位置を揃える。Hub Node回帰34件が成功した。

## 2026-07-13 knowledge-vault 転記（P0定常受入ゲート）

- 転記先: `G:\knowledge-vault\knowledge\dev\self-built-intake-and-layered-pm-oss-selection.md`
- 日時: 2026-07-13 19:23:50 +09:00
- 対象: Hub/Tasksの固有UI変更ではなく、配信資材更新時に同一の安全な再配信手順を使い、Linux実機の最新版反映をP0受入の先頭で確認し、未反映なら未達として完了扱いにしない定常ゲート。

## 2026-07-13 設計書化カバレッジ再監査と読込粒度是正

- 圧縮後の必須初期化は `AGENTS.md` / `PROJECT.md` / `tech-stack.md` / `README.md` / `docs/imp/user-tasks.md` の751行・約44KB。実測13,472 tokenで256Kコンテキストの約5.3%であり、合意した10%以内であることを確認した。
- カバレッジHTMLが参照する38個のローカル正本は最大293行で、見出し単位の最長節も85行だった。現時点に「1機能だけのために500行超を読ませる設計本文」はない。
- 一方、役割別ガイドが受入HTMLを常時セットへ含めると、HTMLのCSS/JavaScriptを含めて10%超になり得た。ガイドを、`imp-tasks`・受入HTML・カバレッジHTMLを作業時／対象ID・対象行だけに限定し、リンク先の自動・再帰全読込を明示的に禁止する形へ修正した。
- 設計書カバレッジの初期全5/5は正本リンクの存在確認に過ぎなかったため、六証拠種別（体験、状態/API、データ、外部境界、運用、受入/回帰）で再監査した。外部境界、運用/復旧、回帰証跡が明示リンクされていない軸を黄色へ下げ、各行に補完内容を表示した。P0実機受入の未達とは混同しない。
- `apps/web/test/design-documentation-coverage.test.mjs` は8/8成功、全ローカルリンク存在、`git diff --check` はエラーなし（既存のCRLF警告のみ）。実データ変更、Linux配信、再インポートは行っていない。

# 2026-07-13 設計書化カバレッジ機能契約の補完

- カバレッジHTMLの10機能について、体験、状態/API、データ不変条件、外部境界、運用/復旧、受入/回帰の六証拠種別を正本へ明示した。P0入口はRaw event storeを実装済みと扱わず、`candidates`へ直接正規化する現行境界へ是正した。
- 現行P0のAI相談にはHTTP・永続化・読み取り専用tool・縮退/復旧を、未実装P1には開始ゲート・fake API/一時DB・rollbackの契約を追加した。Hub/Vikunja/Tasks/再配信も機能別の利用者導線と障害照合を正本へ接続した。
- レビュー用に`design-documentation-review-summary-2026-07-13.html`を追加し、画面×機能ごとの正本、ファイル量、分割、記載の着眼点を10行で一覧化した。見た目・操作感の最終受入は自動回帰と分離し、ユーザーの実画面確認待ちとして残した。
- 結果表の列名を「文書量（ファイル量）」「分割の仕方」「記載上の着眼点（再現条件）」へ明示し、10機能行を静的回帰で固定した。
- `origin/main`へ設計書化・圧迫再調査・review表明確化の5 commitをPushし、リモート参照も`db9601b`で一致することを確認した。
- 設計書カバレッジ静的回帰9件、Python回帰8件、HTMLローカルリンク、`git diff --check`を確認した。全API回帰は、今回未編集の完成度HTMLに対する既存の旧期待文言のため33/34となる。実データ変更、Linux配信、knowledge-vaultへの転記は行っていない。

# 2026-07-13 コンテキスト圧迫の再調査（実装メインセッション3）

- 当該sessionの圧縮直前は244,594 / 258,400 token（94.7%）だった。置換履歴の`input_image`は0件であり、画像残留だけでは今回の早い圧縮を説明できない。
- 大きい初期入力と40KiB級以上のtool出力の反復を構造統計だけで確認し、`docs/guide/context-pressure-session-guideline.md`へ「画像がない圧迫」を追加した。本文、画像内容、Cookie、token、secret、envは表示・記録していない。
- 圧縮後の再計測は40.7%だったが、圧縮1回済みのため判定は黄とした。設計書化と再調査の次回再開packetをdiaryへ残し、次の視覚レビュー・大規模調査・実装フェーズは新sessionで開始する。実データ変更、Linux配信、knowledge-vault転記は行っていない。

# 2026-07-14 コンテキスト圧迫のセッション境界再監査

- 現在更新中のsession JSONLを内容非表示で再集計した。session用ローカル`visualizations`配置先は0 file / 0 byteだが、会話履歴にはbrowser screenshot由来の`input_image`が2 blockある。ローカルファイルの配置自体は圧迫原因ではなく、画像を会話／tool結果へ埋め込むことだけが入力負荷になると確認した。
- 最新実入力は163,347 / 258,400 token（63.2%）だった。圧縮置換履歴の画像は0 blockだが、同一root sessionで圧縮2回済みのため、guideの基準では赤判定とした。tool関連の構造と10KiB以上のrecordは引き続き抑制対象である。
- 調査記録は`docs/imp/context-pressure-investigation-2026-07-13.md`、次回の最小再開packetは`docs/diary/2026-07-14-context-pressure-rotation-packet.md`を正本とする。運用ルールは既存guideで足りるため、同ガイドは更新していない。次のハーネス設計・調査は新sessionから開始する。

# 2026-07-15 Windows knowledge-vault AI取込パイプライン

- WindowsだけがVaultを読み、版管理した`knowledge-vault-task-proposal-v1`で文書要約・根拠付きタスク提案を作るcollectorを実装した。秘密らしい代入行はLLM送信・batch保存前に行単位で伏せる。
- validatorはJSON schema相当のfield/enum、完全一致引用、可視タグmaster、具体的title/todo、有効日付、完了actionを決定論的に検査し、不合格をheldにする。LLMなし/timeout/不正JSONでは明示Next Actionsの未完了項目だけへ縮退する。
- Linux Hub SQLiteに`intake_batches`、`source_documents`、`source_fragments`、`ai_runs`、`candidate_proposals`を追加し、accepted提案だけを`KVAI-*` pending候補へ冪等写像する。Windows絶対root、hidden reasoning、SQLite本体は転送しない。
- 専用SSH鍵、BatchMode、manifest SHA-256、Hub containerの`db_tool.py import-vault-batch`を使うPowerShell/remote helperを追加した。管理画面のLinuxローカルscanボタンは外し、Windows batch source表示へ変更した。
- 自動回帰は新規12件、Hub Node 36件、Hub Python 19件、設計書カバレッジ10件、worker/deploy/backup/Vikunja補助21件が成功した。coverage packageはbundled Pythonにないため、分岐・失敗・統合境界を個別testで固定した。
- 実機`gemma4:latest`は合成Markdownで、完了済み項目を除外し固有名詞・SHA-256を保持した1提案を生成した。実Vault最新3文書dry-runは3 accepted / 2 held / 1文書fallbackで、held 2件は根拠完全一致違反を遮断した。Linux転送・実SQLite変更・GOは行っていない。
- `47d11c3`を`rohto4/my-pj-general`の`main`へPushし、安全再配信scriptでHub `B72EF8979712D2139D4300799A724AC761DD3EA7DFD216743F1D30F32AECB9C4`、Tasks `C4436371FA151399E359089A2338479F3F0F0A740982EE0D8F6CCBF16B934645`をLinuxへ反映した。Hub/Tasks API 200、SQLite integrity `ok`、新lineage table 5件は0行、既存候補・判断・link・Taskも0件を維持した。local LLMの`unavailable`はHub chatだけの残存ブロッカーで、Vault取込は未実行である。
- 目標完了監査で、配信済みのHub / Tasksを`imp-tasks`とブロッカー監査が未配信扱いする文書ドリフトを検出した。失敗する静的回帰を先に追加して進行正本を是正し、Hub Node 48件、Hub Python 19件、worker / infra 23件、PowerShell構文、`git diff --check`を再確認した。残件は外部LLM構成、利用者の視覚判断、確認付き実データ操作だけである。
