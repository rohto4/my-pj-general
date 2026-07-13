# P1実装タスク 2026-07

P1は開始済み。Linux実機接続を外部ゲートとして残しつつ、ローカル実装・回帰・配信bundle準備を先行している。この表はP1の実行順と受入境界を固定する。

## 0. 開始ゲート

- [x] ユーザーがP1の優先順を確認する
- [x] Linux常設環境への接続方法と配信先を確認する
- [x] 現行Hub / Vikunjaのbackupを取得する（Linux実DB、files、config、restore-test済み）
- [ ] P1用branchとrollback基準を作る

## 1. 常設運用・観測

- [x] Hub health / dependency status endpointを設計・実装する
- [x] source sync / reconcile / backupの最終結果を確認できるようにする（`GET /api/observability` と管理画面の運用観測パネル）
- [x] SQLite online backup、生成後quick_check、SHA-256・件数証跡、timestamp世代を実装する
- [ ] backup世代保持数と外部媒体複製をLinux常設環境で自動化する（世代保持は実行済み、外部媒体mirror未設定）
- [x] Vikunja DB / files / configのrestore drillを行う（Linux実DBで件数/hash一致を確認）
- [ ] Ollama / Vikunja停止時の縮退を実機確認する

### 2026-07-12 ローカル証跡

- `/api/health`: 実DBでHTTP 200、DB `ok` / integrity `ok` / candidates 19、Vikunja `not_configured`、local LLM `ok`。
- 到達不能テスト: Vikunja / LLMを設定済み到達不能にし、426ms以内に `degraded`。secret非露出。
- online backup: `tmp/backup/hub/p0-20260712-042201-020225.sqlite`、147456 bytes、integrity `ok`、candidates 19、execution links 0、decisions 0。
- backup SHA-256: `bab37bc817f7d4112abcd6288c0262f2025b1f23ca8457d91c50406f36bb0001`。
- 回帰: Node 20 / 20、Python 3 / 3、check成功。
- Node built-in coverageはserver/db child processをsourceとして列挙しなかったため、表示上の100%をcoverage証拠には採用しない。
- source同期runをknowledge-vault / Slack importへ追加し、Vikunja reconcileも同じrun契約で記録する。直近source別結果とHub backup世代の整合性・SHA-256を`/api/observability`で返す。
- `workers/sync/test_run.py` 4件で、連続2回の冪等、source単位失敗分離、lock排他、systemd timer契約を確認した。
- `infra/backup/rotate-and-mirror.sh` とdaily backup timerを追加し、世代保持・別媒体mirror・files/config退避・`manifest.sha256`生成のLinux実行雛形を固定した。Linux世代生成とrestore drillは完了し、外部mirrorとsystemd登録が未完了。
- `infra/vikunja/build-listening-lounge.sh` / `switch-image.sh` を追加し、custom image buildとstable rollbackのvolume非変更契約を固定した。custom imageのLinux buildは完了し、切替・rollbackは未確認。
- Linux常設環境へ最新Hub bundleを再配信・再buildし、19候補・2 execution linkを保持したままHub/Vikunjaを再起動した。`/api/health`はDB/Vikunja ok、Ollama未接続でdegraded。custom Vikunja imageはbuild済みで、切替・rollbackとsystemd `/etc`登録が残る。
- `/api/observability` にsource / kind / confidence / status / decision / GO / execution完了の運用metricsを追加し、管理画面で5指標を表示する。
- `workers/reconcile/run.py` と15分timerを追加し、Hub復旧後にVikunja再照合を自動再試行できるようにした。Hub停止→復旧のLinux実機証跡は未完了。
- `infra/vikunja/backup-and-verify.py` のrestore drillに対象件数・`execution_links`件数・backup/restore SHA-256を追加し、fixture DBとLinux実DBの別場所restoreテストを通過した。
- 現在の19候補 / decision 0 / execution link 0を基準に、PoCの暫定保留理由を`docs/imp/p1-poc-readiness-2026-07-12.md`へ記録した。
- ローカル完了とLinux実機待ちを`docs/imp/p1-verification-matrix-2026-07-12.md`へ分離して記録した。
- `workers/poc/dry_run.py` で類似候補提示（4組）と部分自動確定dry-run（eligible 0 / blocked 19）を実行した。DB変更・自動GOはない。
- `workers/poc/calendar_dry_run.py` でCalendar一方向eventのdry-run契約を実行した。現行approved候補は0件、`wouldCreate=0`、`externalCalls=0`。認証resource-action matrixとPostgreSQL migration dry-run契約を設計書へ追加し、実DB実行は導入ゲート後に保留した。
- 再開時の回帰確認: worker / backup / Vikunja release / restore / PoCのPythonテスト14件、source sync domain 2件、Vikunja adapter 3件、Hub Nodeテスト20件、Hub checkを通過。Listening Lounge forkは対象unit 24件、theme stylelint、production buildを通過した。

## 2. Vikunja fork配信

- [x] 主要画面の役割、入力、結果、次操作、空状態をinventory化する（`tmp/ui-review/vikunja-listening-lounge/README.md`）
- [x] 共通page guide / empty guide componentをTDDで追加する
- [x] HomeでInbox、project、今日のtask、検索の関係を説明する
- [x] Project Dashboardで「全体確認」と「編集は各view」の関係を明示する
- [x] Inboxを「未整理taskの一時受け皿」と説明し、追加後の整理先を案内する
- [x] List / Table / Kanban / Ganttへ、view固有の用途・操作結果・次の一手を表示する
- [x] task detailへ、title / description / due date / assignee / labels / progressが何に効くかを案内する
- [x] 0 task / 0 bucket / 0 dated task / filter 0件のempty stateを操作付きにする
- [x] guideの表示状態をユーザーが折りたため、必要時に再表示できるようにする
- [x] 1280px / 1920pxで実データと空状態を撮影し、overflow / radius / action clarityを監査する
- [x] `325bc5475` を再現可能にbuildする（Windows production build、Linux custom image build済み）
- [x] custom image build / stable-custom切替の再実行スクリプトを固定する（Linux build実行済み、切替は未確認）
- [ ] stableとcustomを別tag・別portで起動する
- [x] login / dashboard / task / List / Table / Kanban / Ganttを確認する（実データ画面のローカル撮影済み）
- [ ] stableへのrollbackを実施してデータ一致を確認する
- [ ] GitHub pushまたは署名付きartifact保管の正本を決める
- [x] upstream取得、差分確認、再base、回帰、配信の手順を作る（Linux実機での実行は未確認）

## 2.5 Hub AI相談UX

- [x] 1280 x 720の実画面を撮影し、会話・context・composerの情報階層を監査する
- [x] 会話を全幅の主領域、contextを横一列の補助領域へ再構成する
- [x] 接続状態、会話数、確認待ち導線を会話上部の1行へ集約する
- [x] 空会話の案内、書き出し例、provider / model表示を追加する
- [x] 短文メッセージの縦潰れ、status低コントラスト、画面外composerを修正する
- [x] Gemma4実推論とVRAM配置、Hub回帰を確認する
- [x] 左サイドメニューから常時サイド相談を開けるようにする
- [x] 上部サマリを小さくまとめ、独立相談画面を1画面高で会話中心にする
- [x] 大見出しと3段階フローを除去し、入力と送信を同じ行へ置く
- [x] 高さ900px / 650pxでAI相談内の文字と余白を段階的に縮小する

## 3. 定期入口worker

- [x] Web handlerからimport domainを分離する（`apps/web/source_sync.py`をHTTP境界とworkerから共有）
- [x] `source_sync_runs` / cursor / dedupe schemaを設計する
- [x] knowledge-vault adapterをoneshot化する（`workers/sync/run.py`）
- [x] Slack payload adapterを同じ契約へ載せる（payload file入力）
- [x] systemd service / timer / lock / secret境界を作る（`infra/systemd/`）
- [x] 連続2回の冪等実行、source単位失敗、再実行を検証する（worker unittest 4件）

## 4. 実運用データ蓄積

- [ ] candidate作成、編集差分、GO、不要、archive、execution完了を集計する
- [ ] source / kind / confidence / missing別のGO率を確認する
- [ ] 実運用で最初のVikunja linkを作り、Hub実DBに証跡を残す
- [ ] 週次でP1候補の優先度を再判定する

## 5. PoC

- [x] Misskey read-only取得方式をREST / Streaming / Webhookで比較する（比較設計済み、実接続は保留）
- [x] 類似候補を提示するだけの重複束ねPoCをdry-runする（最終判定は実運用データ後）
- [x] 部分自動確定条件をdry-runし、誤候補を記録する（自動GOは未実施、最終判定は実運用データ後）
- [x] Calendar一方向event作成とidempotencyをdry-runする（外部書き込みなし、GO 1件後に最終判定）
- [ ] PostgreSQL schema / migration / rollbackを一時DBでdry-runする
- [x] Better Auth導入前のresource-action matrixを作る（本番認証導入は二人目利用者・共有範囲・競合の観測後に再判定）

## 完了条件

- [ ] `docs/product/p1-phase-brief-2026-07.md` の受入条件をすべて満たす
- [ ] 各PoCが採用 / 保留 / 対象外のいずれかに判定される
- [ ] P2へ送る項目と、P1で運用開始する項目が分離される
- [ ] product / spec / data / arch / ops / imp / diaryが実装実体に同期される
