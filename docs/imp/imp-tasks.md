# 実装待ち

## 最優先: P0フロント受入（2026-07-12再評価）

P0のバックエンド・連携契約は完了しているが、Hub / Vikunjaの画面操作、無効ボタン、読み取り専用責務、最新データ構造のフロント反映が未受入である。次の目標は `docs/imp/next-goal-p0-frontend-completion-2026-07-12.md`、詳細タスクは `docs/imp/p0-frontend-completion-tasks-2026-07-12.md` を正本とする。

- [x] 全button / link / formの静的監査とAPI対応表を作成する（`p0-frontend-operation-audit-2026-07-12.md`）
- [x] Hub / Tasksの編集責務、mirror状態、未接続・接続失敗の次操作をHub UIに反映する
- [ ] Hub候補の保存・保存してGO・GO・不要・アーカイブを、現行プロセスの実画面で受入する
- [x] Hub管理画面の状態ラベル・操作列・2列配置をLinuxへ配信し、4K縦3分割相当で受入する（受入HTML R03）。bundle SHA-256 `B9EB…7B9`照合、Linux再build、`/api/bootstrap` 200、Chrome実画面確認を完了した。
- [ ] 実装済み画面の完成度を黄色枠画像でレビューする（RV01 Dashboard密度、RV02 Gantt空白/時間軸、RV03 Kanban 4列、RV04 task detail読み順、RV05 before/after証跡の画面高）。受入HTML上部から順に確認する。
- [x] Thread Line TLモノグラムを`08-satin-gradient-selected.png`として選定し、同一内容の1254px原寸版と256px高品質縮小版を出力する
- [ ] Thread Line 256px PNGをHubとTasksの共通44px左レールへ実装する（source実装・回帰済み）。Linux配信、幅別実機受入は別断面として残す。原寸PNGは配信しない。
- [x] R04: Hub / TasksをLinuxへ再配信し、Hub `/api/bootstrap=200`とTasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4の維持を確認した。実機Kanbanでguideが残存したため、表示名依存の判定をR05へ分離した。
- [ ] R05: Hub薄橙`Thread Line Hub`、Tasks薄青`Thread Line Tasks`、Inboxアイコン、Kanban guideの`viewKind`抑止をLinuxへ再配信済み。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4の維持を確認済み。残りは強制再読込後の実機見た目受入だけである。手順・チェック欄は `p0-frontend-acceptance-checklist-2026-07-12.html` のR05を正本とする。
- [ ] 定常R06: HubまたはTasksの配信資材を更新した回は、先頭のP0受入チェックR06で`redeploy-p0-frontend.ps1`を実行し、Tasks本文の青・淡青統一とタイトル面を実機確認する。Linux環境が最新版でなければ受入HTMLを赤へ戻し、再配信を先に行う。DB/files/volume削除・再インポートは禁止。
- [ ] 定常R07: R06と同じ再配信で、Tasksの`マスタ管理`統合を実機確認する。左レールは個別3項目を廃止し、統合画面はプロジェクト・ラベル・チームの3セクション、追加・既存編集導線、4K縦3分割相当の横崩れなしを満たす。個別URL・作成／編集フォームは互換性のため維持する。
- [ ] Hub左レール: 主メニューを`ダッシュボード / 簡易日程 / タスクキュー / ワークビュー / 簡易管理`へ変更し、同名のスクロール先と一致させる。通常メニューの相談は除き、AI相談と未実装・非活性の詳細管理を同じ下部ボタン群に置く。回帰は成功し、新しいHub bundleを作成済み。次は定常R06/R07の一行scriptでLinuxへ再配信し、実機受入する。
- [ ] 実VikunjaのHome / Dashboard / Inbox / List / Table / Kanban / Gantt / task detailをguide・empty・action込みで受入する
- [ ] 現行データ構造とHub表示を実データで照合する
- [ ] 1280 / WQHD / 4K縦3分割相当のスクリーンショットと操作証跡を残す
- [ ] RV01 Dashboard: source実装・fork回帰済み。PROJECT OVERVIEW/VIEWSを外し、PJ名サブ表記、処理状況左寄せ、日付未定タスクの完了除外をLinux配信後に1438x715実機で受入する
- [ ] RV02 Gantt: source実装・fork回帰済み。前2週〜向こう2か月の既定範囲、日付変更確認、キャンセル時の巻き戻し、完了バーの強いグレー表示をLinux配信後に実機で受入する
- [ ] RV03 Kanban: source実装・fork回帰済み。guideを外し、4列を維持した無制限縦高・内部スクロールバーなしをLinux配信後に実機で受入する
- [ ] RV04 Task detail: source実装・fork回帰済み。パンくず/タイトル順、4K縦3分割相当で右操作群、説明/コメント文字サイズをLinux配信後に実機で受入する
- [ ] RV05: 1438x715・同一スクロール位置のbefore/afterへ全比較証跡を再取得する
- [ ] U03: 最新bundleでGO/編集/不要/アーカイブ後のHTTP応答、画面の操作ID付き`bootstrap.log`、SQLite `decisions.note` の`operation:<ID>`を同一操作IDで照合する。`refreshBootstrap`は観測API失敗でも判断ログを反映する修正済み。
- [ ] Thread Line左レール: Hubアイコンは銅オレンジ、TasksアイコンはTasks青、輪郭・記号・24px枠・行高は共通化する。sourceとLinux再配信は完了済み、強制再読込後の実機確認待ち。
- [x] P0追加 / 設計書化カバレッジ: `design-documentation-coverage-assessment-2026-07-13.html`で10機能の設計・実装境界・回帰・運用手順を機能単位で対応付けた。`implementation-context-reading-guide.md`に役割別最小読込セットを定義し、Hub UI / Tasks UI / 複数Projectの不足正本を`docs/product` / `docs/spec` / `docs/data` / `docs/arch`へ分離して補完した。棚卸し・設計書化・継続同期のPJ skillを作成・静的検証済み。実データ変更とLinux配信は行っていない。
- [x] 設計書化運用レビュー: 設計書カバレッジHTMLの各行を、体験・状態/API・データ不変条件・責務境界・運用・回帰の六証拠種別で再監査した。一次棚卸しの全5/5を維持せず、証拠が明示リンクされていない軸を黄色へ下げ、各行の補完先を記載した。初期読込は751行・約44KB（実測約13,472 token、256Kの約5.3%）で10%以内。役割別ガイドは、リンク先の自動・再帰全読込を禁止し、対象行・対象見出し・必要な受入IDだけを読むよう修正した。実データ変更とLinux配信は行っていない。
- [x] コンテキスト圧迫調査: 現セッションの圧縮置換履歴、実入力token、画像・添付・tool出力の構造統計を内容非表示で照合し、原因・安全な切替閾値・実装先行／設計書先行を含む再利用skillを記録・検証した（`context-pressure-investigation-2026-07-13.md`、`context-pressure-session-guideline.md`、`.agents/skills/audit-context-pressure/`）。
- [x] コンテキスト圧迫再調査（実装メインセッション3）: 圧縮直前244,594 / 258,400（94.7%）、置換履歴`input_image` 0件、40KiB級以上のtool出力反復を内容非表示で確認した。画像だけを原因とせず、大きい初期入力と全文tool出力を別要因としてguideと調査記録へ反映した。判定は黄で、次の画像・長いログ・広域探索は新sessionへ切り替える。再開packetは`docs/diary/2026-07-13-main-session-3-context-checkpoint.md`を正本とする。
- [x] 設計書カバレッジ補完: 黄色になった行について、外部境界・運用/復旧・回帰証跡を正本（`docs/product` / `docs/spec` / `docs/data` / `docs/arch` / `docs/ops`）へ明示リンクした。P0の実機受入未達はP0/P1完成度星取表で継続管理し、この作業と混同しない。
  - [x] C01: P0入口・Hub候補/判断・Hub画面・ローカルLLM相談について、外部境界、縮退/復旧、回帰/受入の参照先を機能正本へ補完した。`intake-unified-event-model` と `intake-source-adapters` のRaw event store実装範囲は、`source_sync.py` / `server.mjs` / 回帰testの最小読込で照合し、現行P0は`candidates`へ直接正規化すると是正した。視覚スタイルの受入要件は既存の画面要件へ留め、ユーザーの実画面確認を待つ。
  - [x] C02: Hub ↔ Vikunja連携、Thread Line Tasks UI、安全再配信について、利用者導線、fork運用/rollback、画面別回帰とDB保全の根拠を正本化した。
  - [x] C03: 未実装の複数Project連携とP1認証/PostgreSQL移行について、開始前の受入・復旧・外部依存境界を補完した。P0実装済みとは扱わない。
  - [x] C04: 各機能の設計書分割、ファイル量、記載上の着眼点を `design-documentation-review-summary-2026-07-13.html` へ出力し、カバレッジHTMLのリンクと評価を同期した。
  - [x] C05: 設計書カバレッジ静的test 10件、HTMLローカルリンク、Python 8件、`git diff --check`は成功。既存の `apps/web/test/api.test.mjs` は、今回未編集のP0/P1完成度HTMLに存在しない旧期待文言を要求するため1件失敗することを、HEADとの差分なしで確認した。設計書化分と圧迫再調査分は独立commitで記録し、`origin/main`の`db9601b`へPush済みである。別セッションの変更は混在させていない。

Vikunja forkの自動回帰は51 files / 1086 testsが成功済み。実機の最終目視・操作感と、実データを変更するHub判断操作はユーザー受入として残す。

## 現在の状態

- P0バックエンド・連携契約とR03のLinux/Chrome受入は2026-07-12に完了した。P0フロント受入はRV01〜RV05の完成度レビュー、Thread Line画像調整、U03実データ判断、U04/U05の実画面最終判定が残っている。
- 正式監査: `docs/imp/p0-completion-audit-2026-07-12.md`
- 運用runbook: `docs/ops/p0-operations-runbook-2026-07.md`
- P1ブリーフ: `docs/product/p1-phase-brief-2026-07.md`
- P1タスク: `docs/imp/p1-implementation-tasks-2026-07.md`
- P1-AのHub health / SQLite backup / source同期・reconcile観測はローカル実装・回帰済み。Linux常設環境での再build、timer、外部媒体複製、restore drillは未完了。

## 次にCodexが進めるタスク

P1開始のユーザー確認後、次の順で進める。

1. 常設運用・観測・backup / restoreを整える。
2. Vikunja Listening Lounge forkを別tagで配信し、stable rollbackを検証する。
3. knowledge-vaultから定期入口workerを切り出す。
4. Slack payloadを同じworker契約へ載せる。
5. 実運用データを蓄積してから、Misskey・重複束ね・部分自動確定・CalendarをPoCする。
6. PostgreSQL・認証・queueは導入ゲートを満たした場合だけ実装へ進める。

## 2026-07-12 Linux配信（進行中）

- [x] Windows検証済みHub `Listening Lounge` の転送bundleを作成: `tmp/pj-general-web-working-tree.tgz`
- [x] U03のGO／不要／アーカイブ送信前に、実データ・判断ログ変更を明示して確認する画面ダイアログを実装し、Node 28件回帰で確認した。
- [x] Vikunja Listening Lounge forkの転送bundleを作成: `tmp/vikunja-listening-lounge-working-tree.tgz`
- [x] Hub bundle / Vikunja bundleのSHA-256を記録: `docs/guide/linux-listening-lounge-deploy.md`
- [x] 2026-07-14 配信事前確認: `redeploy-p0-frontend.ps1 -DryRun`で現行source-only bundleを再生成し、Hub `79ABF903BD90FFEE452AB71CBFD4831E75E98EE96ECA42E22C47ACD4B2A6DE0E`、Tasks `7B14516023E59960E96DDD204133CC8AAEBDBA7279345FBF33909C5E540F3EB8`を照合した。Hub 34件、補助Python 8件、再配信script 4件の回帰とbundle除外確認は成功。SSH / scp / sudo / Linux実配信はまだ実行していない。
- [ ] Linux上でHub `pj-general` を再buildし、`/api/health` と本流テーマ表示を確認する
- [ ] Linux上でVikunja custom imageを別tagでbuildし、stable rollback可能な状態で切り替える
- [ ] Linux実機でHome / Dashboard / Inbox List / Table / Kanban / Gantt / Task detailとHub導線を受入確認する

Linux側の実行手順は `docs/guide/linux-listening-lounge-deploy.md` を正本とする。現在のCodex環境からは `unibell4@192.168.0.200` のSSH公開鍵認証が通らないため、bundle作成までをこちらで完了し、サーバー側の実行は認証回復後に継続する。

## 後続へ維持する項目

- 製品名、主要ロール名の確定
- `goose` upstream追随手順
- キャパ管理
- マルチエージェント開発用の別PJ
- Codex / MiMo / GLMの互換運用

ユーザー判断は `docs/imp/user-judge.md`、ユーザー作業は `docs/imp/user-tasks.md`、完了記録は `docs/imp/imp-comp.md` を正本とする。
- [ ] P0追加: `p0-vikunja-ux-remediation-2026-07-12.md`に従い、VikunjaのLogin / Home / Dashboard / Inbox / List / Table / Kanban / Gantt / task detailを1280/WQHD/4K縦3分割で再改修し、全画面JPEGのbefore/after証跡を保存する
- [ ] P0追加: Vikunjaの直接起動をProject一覧へ誘導し、Hubからは特定済みProject Dashboard / taskへ直接遷移する。左メニューはProjectのDashboard / List / Gantt / Table / Kanbanを主導線に再編し、標準概要・今後の予定をP0導線から外す
- [ ] P0追加: Hubを複数Projectの正本とし、個人PJを既定表示、個別PJ作成時のVikunja Project冪等作成・候補所属・GO先解決・失敗再試行を実装する（`p0-multi-project-linkage-design-2026-07-12.md`）
- [ ] P0改善: AI要約・抜粋prompt、タグ生成、TODO案を優先表示する候補タイトルのデータ/表示境界を設計し、実装タスクへ分割する（source実装済み: 本文優先抜粋・本文由来要約・既存タグマスタ照合・TODO案優先。既存19件は再インポートせず、新規AI相談候補1件の実機品質受入だけを明示確認後に行う）
