# セッション引継ぎ: P0フロント受入再評価

## このファイルの用途

セッションを切り替える場合の復元用正本です。最新の恒久仕様ではなく、この作業セッションの状態と次の入口を記録します。

## 再開時の必須読み込み順

1. `AGENTS.md`
2. `PROJECT.md`
3. `tech-stack.md`
4. `README.md`
5. `docs/imp/user-tasks.md`
6. `docs/imp/imp-tasks.md`
7. `docs/imp/p0-p1-completion-assessment-2026-07-12.html`
8. `docs/imp/p0-frontend-completion-tasks-2026-07-12.md`
9. `docs/imp/next-goal-p0-frontend-completion-2026-07-12.md`
10. `docs/imp/p1-verification-matrix-2026-07-12.md`
11. `docs/guide/linux-listening-lounge-deploy.md`

## 到達点

- P0のバックエンド・連携契約は完了。Hub本流テーマはListening Lounge。フロント受入は追加P0として未完了。
- Hub / VikunjaのLinux実DBは再起動前後で保持され、Hub candidates 19、decisions 2、execution links 2、Vikunja tasks 2を確認済み。
- HubとVikunjaのDB・files・configのbackup/restore drillを実施し、backup/restore hash一致を確認済み。
- Hub health / observabilityでDB・Vikunjaはok、Ollama未接続時はdegradedになることを確認済み。
- Vikunja custom imageはLinuxでbuild済み。ただしrunning serviceへの切替、stable rollback、件数比較は未実施。
- systemd timer登録、Hub停止→reconcile、外部mirror、候補ライフサイクル1巡回、PoC最終判定は未完了。
- データは消失していないため、再インポートは実施しない。0件またはhash不一致を確認した場合だけ再評価する。
- ユーザー再評価により、P0のバックエンド・連携契約と、P0フロント受入を分離した。画面の全操作、無効ボタン、編集責務、最新DBフィールド反映が未受入のため、P0追加タスクを先に実行する。
- セッション2では、`p0-frontend-operation-audit-2026-07-12.md`へ全button / link / formのAPI対応と無効/読み取り専用の判定を記録した。Hubには編集責務、Tasks状態mirror、未接続/接続失敗の次操作を追加し、Node 21件・Python 5件・構文チェックを通過した。
- 現行ソースを4199番で起動して`/api/bootstrap` 200を確認したが、アプリ内ブラウザは4199番へ到達できなかった。4173番は旧プロセスで現行`/api/bootstrap`を返さない。実画面・実Vikunja・1280/WQHD/4K縦3分割の受入は未完了のまま保持する。データ変更・再インポートはしていない。
- テーマ比較用の旧タスクと旧Hub/Vikunja調和タスクは、Listening Lounge本流とP0フロント受入の正本へ統合済みのため削除した。
- 次回起動の準備として、`infra/deploy/compose.yaml`と`infra/deploy/start-pj-general.sh`を追加した。HubとListening Lounge版Vikunjaを統一Composeで起動するための次期配置であり、Linux実機への配置・実行はまだ行っていない。
- 次回は`infra/deploy/.env.example`を非secretパスだけで設定し、`start-pj-general.sh --dry-run`、一式起動、health/件数確認、Hub/Vikunja実画面受入の順で再開する。

## 2026-07-12 統一起動の初回引継ぎ安全化

- Linuxの`~/pj-general-deploy/infra/deploy`で`./start-pj-general.sh --dry-run`を実行し、Hub/Vikunjaを統一Composeで起動するコマンドが表示されることを確認した。custom Listening Lounge imageは既に存在するため、このdry-runではimage buildは不要だった。
- 旧split Composeの`pj-general` / `vikunja`が同名のまま稼働している可能性があるため、統一起動scriptへ`--adopt-existing`を追加した。通常実行は旧project所有の同名コンテナを検出すると停止し、明示指定時だけ`docker rm -f`でコンテナを置換する。
- `--adopt-existing`はvolume、bind mount上のDB/files、image、データ再インポートに触れない。次は更新済みscriptをLinuxへ反映し、`./start-pj-general.sh --start --adopt-existing --dry-run`で削除対象と起動コマンドを確認してから、同コマンドをdry-runなしで実行する。

## 2026-07-12 統一起動の初回結果

- `--adopt-existing --dry-run`で旧`pj-general` / `vikunja`コンテナだけが置換対象であることを確認後、統一起動を実行した。Hubは起動し、SQLite integrity `ok`、候補19、decision 2、execution link 2を維持している。
- Listening Lounge版Vikunjaは`Restarting (1)`となり、3456番の接続確認に失敗した。データは0件でもhash不一致でもないため、再インポートはしない。コンテナ終了理由をsecret非表示で確認し、原因を修正するまでP0フロント実画面受入はブロック状態とする。
- 終了理由は`service.publicurl is required when cors.enable is true`だった。統一Composeに非secretの`VIKUNJA_SERVICE_PUBLICURL=http://${SERVER_LAN_IP}:3456/`を明示し、Vikunjaだけを再作成して`healthy`とAPI応答を確認する。DB/files/volume、secret env、再インポートには触れない。

## 2026-07-12 実画面受入の再開

- 公開URL設定を反映後、HubとListening Lounge版VikunjaのAPIは正常応答した。Hub実画面でTasks概要（全2、未完了1、完了1）、Vikunja project/task URL、GO済み候補のsync表示、候補編集フォームを確認した。保存・GOは実データ変更となるため未実行である。
- ガントの担当者欄がVikunja assignee objectを`[object Object]`と表示する不具合を検出した。`apps/web/db_tool.py`でusername/name/emailへ正規化する`display_assignee`を追加し、`apps/web/test/test_db_tool.py`へ回帰テストを追加した。Linux Hubへ再配信して確認するまで、Bの保存/GO受入へ進まない。

## 2026-07-12 P0受入のユーザー実行入口

- ユーザーが赤・黄を上から順に解消できる単一HTML `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` を作成した。R01はLinuxへの`db_tool.py`再配信と統一起動、U01-U06はHub/Vikunjaの表示、保存/GO、guide/empty、幅別UI、error/empty/retry受入である。
- HTMLは完了／未達とコメントをlocalStorageへ保存し、「報告プロンプトを生成」からCodexへ貼る形式で出力する。未達は画面名・幅・操作結果をコメントする。保存・GO・Vikunja task変更など実データ操作は、HTML内で明示してユーザーが実行する。
- 星取表のP0 / P0追加は5/5表示を基準にし、未確認は黄、Linux依存ブロックは赤として同HTMLへリンクした。P1再開は、当HTMLの残項目を報告後に判断する。
- Windowsの通常PATHにはNode/Pythonがなかったが、workspace dependency runtimeを使い、Hub Node 24件、Hub Python 7件、統一起動Python 2件の回帰を実行して成功した。以後の実行は付属runtimeを使う。
- Hub実画面は1280px相当とWQHD相当でページ横overflowがなかった。Vikunja Listening Loungeのログイン画面は確認済みだが、認証情報を扱わないため、ログイン後のHome/Dashboard/Inbox/List/Table/Kanban/Gantt/task detailはチェックHTMLのU04からユーザーが受入する。

## 2026-07-12 P0受入フィードバック反映

- ユーザーはR01・U02・U06を完了、U01/U03/U04/U05を未達として報告した。Hubの初期ガント描画はタブ切替後にだけ復帰し、判断ログは欠落または順序が不正だった。
- `app.js`を修正し、Ganttは初期render後の二重animation frame、visibilitychange、resizeで再layoutする。判断ログはDBの最新順を維持し、保存・GO・不要・アーカイブ後にはbootstrapを再取得する。Node 25件・Python 9件が成功し、Linux反映は受入HTMLのR02で行う。
- Vikunjaのtask detail密度、初期Gantt遷移、全主要ページの操作感は、`p0-vikunja-ux-remediation-2026-07-12.md`へ分離した。対象9画面のbefore/after全画面JPEGは指定命名・保存先で新たに取得する。

## 2026-07-12 P0受入: Hub準拠Vikunjaテーマ・初回Gantt修正

- ユーザーのChromeログイン完了により、Vikunja専用の認証待ちブロッカーを解除した。現行Homeを実機確認し、Hubとの差分が鮮やかな青のidentity headerにあることを確認した。
- ユーザー指定に従い、青い`Vikunja / Tasks workspace` identity headerと固有タイトルは維持した。その下をHubの横幅208px、書体、余白、罫線、銅線、藍の選択行、hover時5px横移動へ一致させた。
- `TaskDetailView.vue`は幅1440px以下（4K縦3分割相当）で、細い右操作railを本文下の2列操作面へ再配置するようにした。
- `GanttChart.vue`はrouter初回遷移時に二重animation frame、ResizeObserver、visibility復帰で幅を再計測する。利用者に二度目のタブ切替を要求しない。
- fork固有unit 12件、変更6ファイルのstylelint、production buildをWindowsで再成功。upstream依存のSass非推奨とWorkbox更新確認の警告はあるがbuildは成功した。
- 更新bundleのSHA-256は`E90236D8AED9CB90077270D968EF82AC085B8997D2C7EAD2FDB81D9085CD544F`。青いVikunja identity headerと固有タイトルは残し、その下の横幅208px、書体、罫線、hover時5px横移動をHubへ一致させた。Gantt初回再計測、Kanbanの4列grid、Dashboardの低背化と表示順も同bundleへ含めた。`start-pj-general.sh`へ`--rebuild-vikunja`を追加し、source展開後は一式を安全に再build・起動できる。
- 現在の明示ブロッカーは受入HTMLのR02（Hub再配信）とV01（Vikunja custom image再build）のみ。DB/files/volumeを削除せず、再インポートしない。反映後にChromeで9画面・3幅のbefore/after JPEGと実操作を受入する。

## 2026-07-12 P0 UX断面の再検証

- Hub Node 27件、Hub Python 7件、統一起動Python 2件、Vikunja fork固有unit 12件、変更6ファイルのstylelint、Vikunja production buildをWindowsで再実行して成功した。上流Sassの`@import`非推奨とWorkbox更新確認の権限警告はあるが、build終了状態は成功である。
- Hub bundleは展開後の`app.js`、`db_tool.py`、`server.mjs`、CSS、テストを現行sourceと照合し一致した（`FC4D379A7E5F4CC623BECC245861715DF5A79A28FCF58A5B6E326BD24C2F0B16`）。
- 旧Vikunja bundleは現行sourceとの差異を検出したため配信対象から外した。更新bundleを作り、theme、Navigation、task detail、Gantt、Dashboard、Kanbanの6ファイルを展開比較して一致確認した（`E90236D8AED9CB90077270D968EF82AC085B8997D2C7EAD2FDB81D9085CD544F`）。
- Linux実機の次操作は受入HTMLのR02、V01だけである。反映後の全画面JPEGは`tmp/ui-review/vikunja-listening-lounge/reacceptance/README.md`の台帳に従う。実データ変更、再インポート、volume削除は行わない。

## 2026-07-12 完成度星取表の評価基準修正

- 星取表は10点を切り捨てる表示ではなく、評価値そのものを0〜5の五段階へ統一した。実証・運用・UI/UX・連携・安全は、対応する実機根拠がない限り満点にしない。
- Linux/実機ブロッカーを持つP0追加は該当軸を1〜3/5とし、複数Hub Project連携基盤は設計段階として実装・実証・運用を0〜1/5にした。P1も未運用の軸を過大評価しない値へ見直した。
- クリック編集の保存キーを更新し、旧10点換算のブラウザ保存値が新しい評価を上書きしないようにした。Hub Node 27件の回帰とscorecard script構文確認を通過した。

## 2026-07-12 R02 / V01 Linux反映完了

- ユーザーが受入チェックHTMLのR02とV01を実行した。公開Hubは現行コードの340px固定高、debug表示、有効/停止状態表示を返し、Vikunja APIはListening Lounge custom versionを返す。
- 現在の実機データはHub candidates `19`、decision log `9`、execution links `4`、execution task state `4`。これは受入中の判断操作後の実データであり、再インポートはしていない。
- Linux配信ブロッカーは解消した。残るP0フロント受入は、Hubの初回ガント・判断ログ・Tasks導線（U01/U03）、Vikunja 9画面のguide/empty/action（U04）、1280/WQHD/4K縦3分割のJPEGと操作感（U05）である。

## 2026-07-12 V01再配信の再オープン

- Chromeの1280px実画面でtask detailを確認したところ、右操作railが残り、現行sourceにある本文下の2列操作面が反映されていなかった。Gantt初回表示とKanban第4列は正常に見えるが、V01を完了扱いにする根拠として不足する。
- よってV01を再び赤ブロッカーとし、`E90236D8AED9CB90077270D968EF82AC085B8997D2C7EAD2FDB81D9085CD544F`のbundleをhash確認後にLinuxへ再展開・`--rebuild-vikunja`する。DB/files/volume削除、再インポートは行わない。

## 2026-07-12 V01再配信の旧script分岐

- ユーザーはE902…544Fのhash確認とfork source展開を実行した。`tar: Ignoring unknown extended header keyword 'SCHILY.fflags'`はtarの拡張属性に対する警告で、展開の失敗ではない。
- 続く`unknown argument: --rebuild-vikunja`は、Linuxの`~/pj-general-deploy/infra/deploy/start-pj-general.sh`が旧版であることを示す。公開APIはcustom versionを返し、Hub integrityと実データ（candidates `19` / decisions `9` / execution links `4`）は維持されているが、現行fork sourceを再buildしていないためV01は赤のままとする。
- 次操作はWindows PowerShellから現行`infra/deploy/start-pj-general.sh`を同Linux pathへ転送し、`grep -q -- '--rebuild-vikunja' start-pj-general.sh`で更新を確認してから、同じE902…544F bundleを`--rebuild-vikunja`でbuildする。DB/files/volume削除、再インポート、env表示は行わない。

## 2026-07-12 V01再配信完了

- Linuxで現行起動scriptを反映後、dry-runがVikunja custom imageの`docker build`と統一Compose起動を表示した。本実行はVikunja forkとHubをrebuildし、`pj-general` / `vikunja`を再作成した。
- 起動直後の4173番curl失敗とVikunja health `starting`は起動待ちの一時状態だった。直後の`--status`ではHub SQLite integrity `ok`、candidates `19`、decisions `9`、execution links `4`、Vikunja APIのListening Lounge version応答を確認した。
- Chromeの1280px task detailで、旧い細い右操作railが残らず、タスク操作が本文下の操作面へ移ったことを確認した。V01の赤ブロッカーを解消し、残りはU01/U03/U04/U05の黄の実画面受入・JPEG証跡である。DB/files/volume削除・再インポートはしていない。

## 2026-07-12 U01 Hub再受入完了

- Hubを初回読込からChromeで確認し、Tasks概要の4件（未完了2 / 完了2）、Vikunja task link、Hub/Tasksの編集責務、Vikunja青の`Tasks側を開く`導線、最新順の判断ログを確認した。
- `#worker`のガントは初回表示で週表示、`L1 Triggers`のtimeline、担当`unibell`、進捗`100%`を表示した。以前の「タブ切替後だけ復帰する」症状は再現しなかった。
- U01を完了へ更新した。実データを変更していない。残るP0フロント受入は、実データ変更前の確認が必要なU03と、Vikunja全画面・3幅・JPEG証跡のU04/U05である。

## 2026-07-12 Vikunja U04/U05 agent再受入証跡

- ChromeでDashboard / Gantt / Kanban / task detail / List / Table / sidebarを再巡回し、`tmp/ui-review/vikunja-listening-lounge/reacceptance/`へNo.01〜09のbefore/after JPEGを保存した。
- WQHD（01/02/03）、1280px（05/06/07/09）、4K縦3分割相当1440px（04/08）でdocument横overflowはすべて`false`だった。GanttはWQHDと1280pxの初回遷移でdate range / timelineを表示し、task detailは1440pxで操作railが本文下の操作面へ移った。
- これは表示・遷移・layoutの客観証跡であり、taskの編集・完了・期限・担当変更はしていない。U04/U05はユーザーの最終目視・操作感判断を待つ黄色として、チェックHTMLにファイル番号と幅を残した。

## 2026-07-12 Hub管理画面の密度・操作列修正

- ユーザーの4K縦3分割相当の実画面指摘を反映した。状態ラベルを各管理cardのタイトル横へ移し、`取込`と`無効化` / `有効化`を縦積みの操作列にした。
- 管理gridは常時2列へ変更し、DOM順を入口設定・タグマスタ・プロンプトテンプレート・取り込み対象・ロール表示・AI確定方針に並べ替えた。これにより狭い作業幅で設定cardを優先し、ロール／方針は後段3行目になる。
- Node回帰28件が成功。U03のGO／不要／アーカイブ送信前確認ダイアログを実装した。Hub bundle `tmp/pj-general-web-working-tree.tgz`を更新し、SHA-256は`B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9`。R03でHub serviceだけをLinuxへ再build・再作成するまで赤とする。DB/files/volume・Vikunja image・再インポートには触れない。

## 2026-07-12 P0受入: Hub情報密度・状態表示の修正

- 入口別の量と候補の種類が判断ログの高さに連動して縦に伸びる問題を修正した。両方を340px固定高、5行均等、必要時だけ内部scrollへ変更した。
- Tasks側を開く導線は、接続済み時にVikunja青の専用ボタンとして強調する。未接続時は誤操作防止のdisabled状態を維持する。
- `P0ルール`、管理画面のSQLite表示、運用観測のstatusを薄いオレンジのdebug表示へ統一した。
- 管理のsource等は、有効時に`有効`ラベル＋`無効化`ボタン、停止時に`停止中`ラベル＋`有効化`ボタンを表示する。
- Hub Node 27件、Python 9件を成功。更新Hub bundle SHA-256は`FC4D379A7E5F4CC623BECC245861715DF5A79A28FCF58A5B6E326BD24C2F0B16`。R02でLinux再配信後に実画面受入する。

## 2026-07-12 Vikunja導線判断

- Vikunjaの単独起動はInbox Dashboard固定にせず、複数Project前提のProject一覧を既定入口にする。
- Hubからはexecution linkで解決できるProject Dashboardまたはtaskへ直接遷移する。対象が解決できない場合だけProject一覧へ戻す。
- P0導線から標準概要・今後の予定を外し、Project配下のDashboard / List / Gantt / Table / Kanbanを左メニューの主導線へ再編する。Project・Label・Teamの作成/一覧は管理入口へ統合するが、旧route/APIは互換目的で維持する。

## 次の正本

## 2026-07-13 P0再配信・受入チェック断面

- 最新の実行入口は`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`のR04。Hub `4AF5C14E7F180B2C31E9C9E4C119B7D315CE53DDA57C76AF226F3457FC5F3AC6`、Tasks `BC0C8B8B7462FA5524C973B690AFC0C083DD34B7A55C54E55B5D227993D64C7A`を照合してから一式を再buildする。
- R04はThread Line 44px左レールとRV01〜RV04 source修正を配信するだけであり、DB/files/volumeの削除、再インポート、env内容の表示はしない。Linux実行後に`/api/bootstrap`と`/api/v1/info`がともに200になったことを確認する。
- P0受入HTMLのU01は未達のままとし、R04反映後に初回遷移からHubガントが崩れないことを再受入する。RV05は1438x715の同一条件でbefore/afterを撮影し直す。

## 2026-07-13 星取表の実態再評価

- 星取表のP0本体も、実装済みの契約・データ・回帰とは分けて、未受入のUI/UX・実画面連携・安全確認を3〜4/5かつ黄色へ下げた。ブロッカーが残る対象に5/5を残さない。
- `現在の作業`とP0追加行はR04を赤、RV01〜RV05/U01〜U03/U05を黄色で示す。正本は`docs/imp/p0-p1-completion-assessment-2026-07-12.html`である。

## 2026-07-13 U02 新規候補の品質改善

- 新規knowledge-vault / Slack候補は本文優先の抜粋・要約と、既存タグマスタに照合するタグ選択へ変更した。AI相談の候補promptも、推測や定型句を避け、TODO案を具体的な実行タイトルにするよう更新した。
- 既存19件への再インポートはしていない。R04後に、明示確認を得てから新規AI相談候補を1件だけ作り、実機品質を確認する。

## 2026-07-13 R04前の公開画面確認

- Chromeの読み取り専用確認で、Hubは旧P0表示、Tasksは旧Vikunja identityとKANBAN VIEW guideを返した。R04未配信が実画面でも確認できるため、受入HTMLと星取表では赤ブロッカーを維持する。

- Thread Line Workspaceの画面・ブランド・導線の確定要件は`docs/product/thread-line-workspace-requirements.md`。TLモノグラムの最終選定だけは`docs/imp/user-judge.md`の`UJ-THREAD-LINE-01`で待機する。
- TLロゴの画像生成は別セッションへ切り出す。選好画像、採用方向、次の生成指示は`docs/product/thread-line-logo-handoff-2026-07-12/README.md`に集約した。
- 実装セッション再開時点で、Hub Node 28件、Python 7件、星取表・受入HTML script構文、`git diff --check`が通過した。R03の現行bundle SHA-256は`B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9`で、現在はR03も実機確認済み。残りはU03/U04/U05とThread Line画像調整である。
- 10軸評価表: `docs/imp/p0-p1-completion-assessment-2026-07-12.html`
- 評価表の正本はHTML。Markdownプレビュー前提へ戻さず、星取表の視認性・クリック編集・要確認セルを維持する。
- P0フロント追加タスク: `docs/imp/p0-frontend-completion-tasks-2026-07-12.md`
- 次の目標: `docs/imp/next-goal-p0-frontend-completion-2026-07-12.md`
- P1次目標（P0完了後に再開）: `docs/imp/next-goal-p1-real-operations-finish-2026-07-12.md`
- P1タスク: `docs/imp/p1-implementation-tasks-2026-07.md`
- P1監査: `docs/imp/p1-completion-audit-2026-07-12.md`
- 実機検証: `docs/imp/p1-verification-matrix-2026-07-12.md`

## 2026-07-12 完成度レビューの黄色枠証跡

- 「残タスクではないが十分な出来かを判断したい」箇所を、既存のVikunja実機JPEGからRV01〜RV05へ切り出し、`tmp/ui-review/p0-review-2026-07-12/`へ黄色枠付きPNGとして保存した。
- RV01はDashboardの処理状況・30日カレンダー・未日程/最近のタスク/ビュー、RV02はGanttのguide・時間軸・下部空白、RV03はKanbanの4列・内部scroll・下部空白、RV04はtask detailのタイトル/メタ情報・説明・コメント・操作面、RV05はbefore/afterの画面高不一致を対象とする。
- `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`の最上部へRV01〜RV05を追加し、完了/未達の排他的checkbox、コメント、報告プロンプト生成の流れでユーザーが上から判断できる状態にした。実データ変更は行っていない。
- 星取表のP0追加へ「完成度レビュー（黄色枠 RV01〜RV05）」を追加し、U/O/Xなど未証明軸を要確認として表示する。Thread Line画像調整とR03 ALLOKはレビュー対象から外した。

## 2026-07-12 再受入JPEGのHTML内ギャラリー化

- ユーザー要望に合わせ、受入チェックHTML内へ再受入JPEG18枚のサムネイルを表示し、クリックで原寸寄りの拡大表示を開けるようにした。
- 拡大表示は閉じるボタン、背景クリック、Escキーに対応する。元JPEG・実データ・受入チェックの入力値は変更していない。
- `apps/web/test/p0-checklist-gallery.test.mjs`が成功。HTML inline script構文も再確認する。

## 2026-07-12 ユーザー再受入報告とTasksアイコン配色

- ユーザーが受入HTMLをRV01〜RV05、A01〜U06まで確認した。A01/R01/R02/R03/V01/U04/U06は完了、RV01〜RV05/U01/U02/U03/U05は未達としてコメントを受領した。
- RV01〜RV05の解消手順を受入HTMLのdefaultState、星取表、`imp-tasks`、`p0-frontend-completion-tasks`へ同期した。RV01〜RV05は黄色のユーザー判断待ちで、Thread Line画像保留は別境界のまま維持する。
- U03について現行コードを確認したところ、`update_status` / `update_candidate` / `prepare_execution` は各判断をSQLite `decisions`へ記録し、bootstrapは`d.id desc`で返す。判断後の`refreshBootstrap`がbootstrapとobservabilityを`Promise.all`していたため、観測APIだけの失敗で判断ログの再描画まで止まる経路を修正した。最新bundleでHTTP応答・bootstrap.log・SQLite decisionsを同一操作IDで照合する作業はユーザー実機確認待ち。
- Tasks左レールはHubと同じ記号・輪郭・24px枠・行高を使い、Tasks側だけ`--threadline-tasks-accent`の青へ変更するfork source修正を追加した。Hubは銅オレンジのまま。Linux再配信・実画面確認は未実施。

## 遠隔操作の注意

- 接続先はLinux実機 `unibell4@192.168.0.200`。ユーザーのSSHセッションが利用できる場合は、そこを優先する。
- Docker操作は必要に応じて`sudo docker`。sudoパスワードはチャットに入力しない。
- env全文、`docker inspect`のsecret項目、秘密鍵内容は絶対に出力しない。
- systemd `/etc`への登録は、ユーザーの対話SSH端末でsudo実行する前提にする。
# 2026-07-12 実装セッション継続メモ

## 2026-07-13 RV01〜RV04実装断面

- ユーザーの完成度レビューに対し、Vikunja forkのDashboard/Gantt/Kanban/task detailをsource側で修正した。RV01〜RV04はテスト先行で実装し、fork全unit 51 files / 1090 testsを通過した。
- まだLinux custom imageへ配信していない。次の配信後、同一1438x715条件のbefore/after JPEGを保存し、Dashboard/Gantt/Kanban/task detailの実画面を再受入する。RV05はこの証跡再取得のため未達のままとする。

## 2026-07-13 Thread Line縮小ロゴの実装断面

- ユーザーが確定した縮小ロゴ`thread-line-mark-master-256.png`を、HubとVikunja Listening Lounge forkの左レールへ組み込んだ。原寸PNGは配信せず、256px版のみを各アプリのassetとして持つ。
- 両アプリの左レール識別は44px正方形、1px輪郭、6px藍色オフセット、`object-fit: cover`で揃えた。Hubは銅の輪郭、TasksはTasks青の輪郭で区別する。
- source側のHub Node 31件とVikunja fork 51 files / 1087 testsは成功。Linux再配信・再build・実画面確認は次の明示的な配信断面で行う。DB/files/volume削除・再インポートは不要。

- ユーザーがR03の現行Hub bundle（SHA-256 `B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9`）をLinuxへ展開し、`pj-general`だけをbuild・再作成した。image buildとcontainer Startedは成功した。
- 起動直後の`Up Less than a second`時点でhealth/bootstrapをcurlしたため接続失敗。待受ループ後に再確認する。Vikunjaは再作成しておらず、今回のHub R03とは切り分ける。
- 待受ループ後、Hub `/api/bootstrap` が`200`となった。R03のLinux配信・起動は完了し、Chrome管理画面の状態ラベル・操作列・2列配置確認も完了した。
- ユーザーがChromeでR03を確認し、状態ラベルの位置、取込／有効化／無効化の縦並び、管理カードの2列配置、4K縦3分割相当の横崩れなしをALLOKと報告した。R03を完了へ同期した。
- Thread Line画像は追加調整のため正式SVG実装を保留。選定履歴と`07-silver-white-glass-selected.png`は保持し、今回作成途中だったSVGは配信対象にしない。

## 2026-07-13 U03 操作ID照合を追加

- U03の実データ受入を曖昧にしないため、Hubは編集・GO・不要・アーカイブごとに操作IDを作り、HTTP応答、画面の判断ログ、SQLite `decisions.note`へ同じIDを残すようにした。観測API失敗でもbootstrapの判断ログを更新する既存ガードは維持する。
- Node 31件、Python 8件、`git diff --check`を通過した。Hub bundleは`E8EBE20B4C7913437BF8C2FE9F83D7B5FD656C2DBC7257D6A95B138FE9B74AA7`へ更新。R04でLinuxへ配信後、ユーザーが新規検証候補で実データ変更前の確認を得てから受入する。既存19件の再インポートはしない。

## 2026-07-13 U03 HTTP表示を追加

- Hubの判断完了通知へHTTP状態と操作IDを表示し、受入HTMLのU03だけを見ながら、API成功・判断ログ・SQLiteを照合できるようにした。
- Hub bundleは`4AF5C14E7F180B2C31E9C9E4C119B7D315CE53DDA57C76AF226F3457FC5F3AC6`へ再更新。R04でLinux配信後の実機受入まで、P0追加の実証・運用・UI/UX・連携セルは黄色または赤のまま維持する。

## 2026-07-13 R04完了後のR05再配信断面

- R04はLinux再配信済み。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、Hub実データcandidates 19 / decisions 9 / execution links 4を確認し、再インポートはしていない。
- 実機のKanbanでguideが残った。原因は表示名に依存した抑止条件であり、`viewKind === 'kanban'`へ置換して回帰テストで固定した。
- 左レールの最終要件として、Hubは薄橙の`Thread Line Hub`だけ、Tasksは薄青の`Thread Line Tasks`だけを表示し、両方とも44px TLマークを維持する。TasksのInbox等Project行にはTasks青アイコンを置く。
- 次のユーザー操作は、受入HTMLのR05にある`redeploy-p0-frontend.ps1`一行の実行だけ。SSH/sudoの対話パスワード以外は不要で、scriptがhash照合、source-only展開、再build、Hub / TasksのHTTP 200を行う。完了後はHub/Tasksを強制再読込し、左レールとKanban guide非表示を受入する。
- 初回R05 scriptはWindows PowerShellからSSH TTYへhash環境変数を渡せず、展開前のhash照合で停止した。remote shellの位置引数へ変更し、script回帰と`-DryRun`で修正を確認した。ユーザーは同じ一行を再実行すればよく、失敗時点で実データ・DB/files/volumeは変更されていない。
- 標準入力経由の位置引数も対象SSHで対話shellとして扱われたため、helperを転送して通常のSSH remote commandとして実行する方式へ切り替えた。sudoはTTYから入力でき、hash不一致なら展開前に停止する。script回帰2件と`-DryRun`を再確認した。
- remote commandの引数差異を避けるため、scriptはHub/Tasks hashだけの一時manifestを転送し、Linux helperは`/tmp/pj-general-p0-redeploy-hashes.txt`から期待hashを読む。manifestはsecretを含まず、Windows側は終了時に削除する。

## 2026-07-13 R05再配信成功

- `redeploy-p0-frontend.ps1`がHub/Tasks bundleのhash照合、source-only展開、再build、待受を完走した。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`を確認し、候補19 / decision 9 / execution link 4を維持した。再インポート、DB/files/volume削除、secret表示は行っていない。
- 次の断面は配信ではなく、Hub/Tasksを強制再読込してThread Line左レールとKanban guide非表示を確認するR05実機受入である。失敗なら受入HTMLに幅・画面・差分を記載して戻す。

## 2026-07-13 R06 Tasks本文のアクセント統一

- R05反映後の実機で、Tasks本文にHub由来のオレンジが残ることを確認した。Tasksは共通の直角形状・罫線・情報密度を維持し、本文アクセントだけをTasks青`#5176d8`と淡青`#89b8ff`に統一する。
- source、テーマ回帰18件、stylelint、production build、source-only bundle作成まで完了した。更新Tasks bundle SHA-256は`B841C75C21D6D4B10BA262189B9533287C30E23A6D0C0E3FCA73A836359A57DE`である。
- 次のユーザー操作は、既存の`redeploy-p0-frontend.ps1`を一行実行することだけ。scriptがhash照合、Hub/Tasks再build、両API 200確認を行う。実機でオレンジ残存なしを確認するまで、R06は赤ブロッカーとして受入HTMLと星取表へ残す。
- 同じレビューで、Tasksの薄青が識別リンク全体を塗っていることも確認した。Hubと同じくTLマーク右のタイトル面だけを薄青にする修正をR06へ追加し、Tasks bundle SHA-256は`4EB8CF69FDF03FE7586CCD95E94E80B36293CD2B612AD7B14373D184097CECCA`へ更新した。

## 2026-07-13 Tasksマスタ管理統合（R07準備）

- Tasksの左レールからProject／Label／Teamの個別3項目を外し、短い統合名称`マスタ管理`を採用した。プロジェクト・ラベル・チームを3セクションで表示し、それぞれの追加、既存Projectの遷移、既存Teamの編集、既存Labelの確認導線を一画面へまとめた。個別URLと作成／編集フォームは後方互換のため残す。
- Tasksテーマ回帰19件、stylelint、production buildを確認し、source-only bundleを`D166BBCBCC56414D00E4278C4710B91FC750054902CEAF9DA090D82DCF39B85D`へ更新した。Linuxでは既存の`redeploy-p0-frontend.ps1`一行だけでR06/R07を同時配信できる。DB/files/volume削除・再インポートは行わない。

## 2026-07-13 Hub左レール・受入チェックの再編

- ユーザー要件として、Hub左レールの主導線を`ダッシュボード / 簡易日程 / タスクキュー / ワークビュー / 簡易管理`に確定した。スクロール先の見出しも同名へ統一する。
- 通常メニューの「相談」は廃止し、AI相談だけを下部のサイドボタンとして残す。同じボタン骨格で、未実装・非活性の`詳細管理`をAI相談の下に置く。
- R06/R07は一回限りの赤い配信タスクではなく、HubまたはTasksの配信資材を更新した回に最初に確認する定常ゲートへ変更した。最新Linux反映でなければ受入HTMLの未達を選んで赤へ戻し、一行の安全な再配信scriptからやり直す。
- 再配信scriptは実行直前にローカルsourceからHub / Tasks bundleを再生成する。Windowsで古い`tmp/*.tgz`を手作業更新する工程は不要で、ユーザーは一行scriptとSSH / sudoの対話パスワード入力だけを行う。新Hub左レール資材のLinux反映前はR06/R07を赤のまま保持する。
- Hub左レールのscroll先ずれは、`/#...`リンクと手計算offsetの組合せがセクション共通のscroll marginを無視していたことが原因だった。`#...`へ統一し、hashと画面内ボタンが共通scroll処理を通るよう修正した。Node回帰34件を確認済み。次回R06でLinuxへ配信する。
