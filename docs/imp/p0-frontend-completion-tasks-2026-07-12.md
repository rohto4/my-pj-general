# P0追加タスク: Hub / Vikunjaフロント受入完了

## 再評価

P0のバックエンド、SQLiteデータ構造、GO・Webhook・reconcileの連携契約は完了している。一方、画面に表示されるすべての情報が編集対象なのか、どの画面で操作し、何が変わるのかのフロント受入が未完了である。

したがって、P0は次の2層に分ける。

| 層 | 状態 | 意味 |
| --- | --- | --- |
| P0契約・データ | 完了 | 候補・判断・GO・Vikunja task・状態mirrorのAPI/DB契約 |
| P0フロント受入 | 未完了 | 実画面の操作、適用結果、無効ボタン、責務説明、最新データ反映 |

## 現在確認できる実装上の事実

- `apps/web/index.html` の `Tasks側を開く` とガントの外部リンクは、初期状態で `is-disabled` / `aria-disabled="true"` になっている。
- `apps/web/app.js` はVikunja概要の `project.url` が返った場合だけ、上記リンクを有効化する。接続失敗時の理由表示はあるが、接続復旧後の再操作と実画面受入が未証明である。
- ガントは `ganttTasks` を描画するだけで、Hub内の編集操作は持たない。画面上の `Tasks側で管理` という境界説明が必要である。
- 候補詳細にはHub側の編集 / GO / 不要 / アーカイブ操作があるため、これらは実画面で保存結果・一覧反映・エラー回復まで受入する必要がある。

## 操作責務の暫定境界

| 表示・操作 | 編集場所 | P0追加で確認すること |
| --- | --- | --- |
| Hub候補のタイトル・summary・TODO・schedule・tags | Hub | 編集、保存、保存してGO、失敗時の再表示 |
| Hubの確認待ち判断 | Hub | GO / 編集 / 不要 / アーカイブと判断ログ |
| Tasks側概要・件数・直近task | 原則Hubは読み取り | loading / 未接続 / 取得失敗 / 正常時の導線と説明 |
| Vikunja taskのtitle・期限・担当・進捗 | Vikunja | Hubから「Tasks側で編集する」ことが明示され、リンクが機能する |
| HubのTasks連携ガント | 原則読み取り | 固定データなし、期限・状態の出所、空状態、Tasks側リンク |

「Tasksの項目もHubで直接編集する」ことを要件にする場合は、上記境界を変更するユーザー判断が必要であり、別の追加仕様として扱う。

## 実装タスク

### A. 表示・操作の全数監査

- [x] Hub / Vikunjaの主要画面を画面単位でinventory化する（`p0-frontend-operation-audit-2026-07-12.md`）
- [x] すべてのbutton / link / tag / formについて、操作結果とAPI endpointを対応付ける
- [x] 無効リンク、仮ボタン、クリックしても状態が変わらない操作を洗い出す
- [x] 無効理由を「未接続」「読み取り専用」「設定待ち」のいずれかで表示する
- [ ] loading / empty / error / successの4状態を各主要操作で確認する

### B. Hub候補・判断フローのフロント完了

- [ ] 候補詳細の編集項目が最新DBフィールドと一致する
- [ ] 保存、保存してGO、GO、不要、アーカイブの結果を画面へ即時反映する
- [ ] API失敗時にボタン状態・エラー・再試行導線を壊さない
- [ ] GO済み候補のexecution link、sync state、task IDを常に表示する
- [ ] 追加・編集後の一覧、件数、判断ログ、ガントへの反映を確認する

### C. Hub ↔ Vikunja UI結合

- [ ] Tasks概要の正常 / 未接続 / 接続失敗 / 0件を実画面で確認する
- [ ] Tasks側を開く、直近taskを開く、更新ボタンの遷移・再取得を確認する
- [ ] Hubで編集できる項目とVikunja側で編集する項目を画面内に明記する
- [ ] Vikunja側の完了・期限・担当・進捗がHubへ反映されることを表示で確認する
- [ ] Hub停止・Vikunja継続・復旧後reconcileの表示を確認する

### D. Vikunja frontendの操作導線

- [ ] Home / Dashboard / Inbox / List / Table / Kanban / Gantt / task detailの主操作を確認する
- [ ] 各ページの「入力 → 変化 → 次の操作」をguideで説明する
- [ ] 0 task / 0 bucket / 0 dated task / filter 0件のempty actionを確認する
- [ ] 1280px、WQHD、4K縦3分割相当で、主操作が画面外へ逃げないことを確認する
- [ ] HubとVikunjaを混同しないidentity headerとアクセントを確認する

### E. 最新データ構造との同期

- [ ] API / DBの最新フィールドが画面の表示・編集・並び替えに漏れなく反映される
- [ ] staleな固定sample、旧label、旧URL、旧状態名を除去する
- [ ] frontend build、unit、stylelint、実画面操作を同じcommitの証跡にする

## 2026-07-12 セッション2の進捗

- 全操作の静的inventory、API対応、無効/読み取り専用理由は `p0-frontend-operation-audit-2026-07-12.md` に記録した。
- Hub画面にはHubとTasks側の編集責務、Tasks mirrorの状態、未接続/接続失敗時の次操作を追加した。
- Node 28件、Python 7件の回帰と構文チェックは成功した。R03のLinux配信・Chrome確認は完了し、実Vikunjaの最終目視と実データ判断操作は未完了である。
- 現在はB「Hub候補・判断フローのフロント完了」を実画面で受入中。R03の4173番は現行bundleで再配信済みで、`/api/bootstrap` 200と管理画面の幅別確認を完了した。U03の実データ判断操作は実行前確認付き、U04/U05はユーザーの最終画面判定として残す。開始・検証・保留の表示はHTML星取表の`現在の作業`を正本として同期する。
- 実装済みだが完成度の判断が必要な画面は、`tmp/ui-review/p0-review-2026-07-12/`の黄色枠画像RV01〜RV05へ分離した。Dashboardの密度、Ganttの空白/時間軸、Kanbanの4列・内部スクロール、task detailの読み順、before/after証跡の画面高を、受入HTMLの上部からユーザーが順にレビューする。実データ変更は行わない。
- 再受入JPEG一覧は受入HTML内へbefore/afterサムネイル18枚として埋め込み、クリック拡大・閉じる・背景クリック・Escキーを実装した。元JPEGと実データは変更しない。

## 2026-07-12 ユーザー再受入報告の解消タスク

- RV01 未達: DashboardのPROJECT OVERVIEW/VIEWSを削除し、PJ名サブ表記、処理状況の左半分寄せ、日付未定タスクの完了除外を実装する。
- RV02 未達: Ganttの既定Date Rangeを前2週間〜向こう2か月にし、日付スライド時の確認/キャンセル巻き戻し、完了済みバーのグレー強調を実装する。
- RV03 未達: Kanban guideを削除し、4列の表示を維持したまま列の縦高を制限せず内部スクロールバーを消す。
- RV04 未達: task detailのパンくず/タイトル順、狭幅の右操作群、説明/コメントの文字サイズを調整する。
- RV05 未達: 1438x715・同一スクロール位置・同一条件のbefore/afterへ全比較証跡を再撮影する。
- U01 未達: 初回Gantt崩れを再現条件付きで切り分け、Vikunja主要画面のスタイル修正をRV01〜RV04へ分割して実装する。
- U02 未達: AI要約/抜粋promptとタグ生成ロジックの改善タスクを別断面で積む。候補タイトルはTODO案優先を維持する。
- U03 未達: 最新Hub bundleで各判断操作後のHTTP応答、画面に表示される操作ID付き`bootstrap.log`、SQLite `decisions.note`の`operation:<ID>`を同一操作IDで照合する。観測API失敗で画面更新が止まらないHub修正と操作IDの永続化・表示は実装済み。
- U05 未達: RV05の同一サイズ証跡取得後、1280/WQHD/4K縦3分割を再受入する。
- 統一起動を実行した結果、Hubは起動しSQLite integrity `ok`、候補19、decision 2、execution link 2を保持した。一方、Listening Lounge版Vikunjaは起動直後にrestartしている。データを変更せず、コンテナ終了理由の確認を先に行い、正常起動後にBの実画面受入へ戻る。
- コンテナログから、CORS有効時に必須の`service.publicurl`が未設定と特定した。`infra/deploy/compose.yaml`で非secretの`VIKUNJA_SERVICE_PUBLICURL=http://${SERVER_LAN_IP}:3456/`を明示する。更新Composeを反映して正常起動するまで、P0実画面受入はブロック状態を維持する。
- 公開URL設定後、Listening Lounge版Vikunja `2.3.0-pj-general-listening-lounge` のAPI応答、HubのTasks概要（全2件・未完了1件・完了1件）、project/task link、Hub候補編集フォームを実画面で確認した。ガントの担当者がVikunjaのassignee objectを`[object Object]`と表示する不具合を検出し、文字列への正規化と回帰テストを追加した。再配信・再確認後に保存/GOの受入へ進む。
- `apps/web/test/api.test.mjs` 24件、`apps/web/test`のPython 7件、`infra/vikunja/test_recover_pj_general.py` 2件を、ワークスペース付属Node/Python runtimeで再実行して成功した。P0受入チェックHTMLも回帰対象に含む。
- 実機ブラウザでHubを1280px相当（clientWidth 1230）とWQHD相当（clientWidth 2545）で確認し、いずれも`scrollWidth == clientWidth`でページ全体の横overflowがないことを確認した。VikunjaはListening Loungeのログイン画面まで表示確認済みで、Home以降はユーザーの認証済みセッションでU04として受入する。
- ユーザー受入報告: R01、U02、U06は完了。U01はHubガントが初回表示で崩れタブ切替後に復帰、U03は判断ログの欠落または順序不正、U04はVikunja主要画面UX・初期Gantt遷移、U05は幅別UI調整観点の追記待ちとして未達だった。
- U01/U03に対し、Hubは`visibilitychange` / `resize` / 二重animation frameでGanttを再layoutし、判断ログをDBの最新順で表示するよう修正した。保存・GO・不要・アーカイブ後は`/api/bootstrap`を再取得してDB正本のログを再描画する。Node 25件、Python 9件の回帰成功。R02として`app.js`再配信後に実画面再受入する。
- Vikunja全ページUXと全画面JPEG証跡は`p0-vikunja-ux-remediation-2026-07-12.md`へ分離した。AI要約・抜粋の生成prompt、タグ生成ロジック、TODO案を優先表示するタイトル方針は、実装前にデータ保持・表示境界を確認する改善タスクとして次走へ積む。
- TODO案を候補の表示名・判断ログ・ガント・Vikunja task作成のtitleとして優先するよう実装した。元の入口titleは候補編集の参照値として保存を維持する。Node 25件、Python 9件の回帰成功。AI要約・抜粋promptとタグ生成は別途改善タスクとして残す。
- R04をLinuxへ再配信し、Hub `/api/bootstrap=200`とTasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4の維持を確認した。公開Kanbanではguideが残ったため、ローカライズされる表示名ではなく`viewKind === 'kanban'`でguideを抑止するR05へ修正した。
- R05のsourceではHub左レールを薄橙の`Thread Line Hub`、Tasks左レールを薄青の`Thread Line Tasks`へ揃え、旧副題を除去し、Inbox等のProject行にTasks青アイコンを追加した。Hub Node 31件、Tasksテーマ17件、型検査が成功している。2026-07-13に`infra/deploy/redeploy-p0-frontend.ps1`でLinux再配信を完了し、Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4の維持を確認した。残りは強制再読込後のR05実機見た目受入だけである。
- R06として、実機で残ったHub由来のオレンジをTasks本文から除去し、primary/link/focus/選択行/left rail/button/card/task/dashboard/calendarをTasks青`#5176d8`／淡青`#89b8ff`へ統一した。さらに、薄青の識別面はHubと同じくTLマーク右のタイトル面だけを塗り、識別リンク全体は塗らない。テーマ回帰18件、stylelint、production buildは成功し、更新Tasks bundle SHA-256は`4EB8CF69FDF03FE7586CCD95E94E80B36293CD2B612AD7B14373D184097CECCA`。Linux再配信と実機受入はR06として残す。
- R07として、Tasks左レールのProject／Label／Teamを`マスタ管理`へ統合した。`マスタ管理`は10文字以内の名称で、同一画面にプロジェクト・ラベル・チームの3セクションと各追加導線を置く。既存の個別URLと作成／編集フォームは直接リンク・後方互換のため残す。テーマ回帰19件、stylelint、production buildを成功させ、更新Tasks bundle SHA-256は`D166BBCBCC56414D00E4278C4710B91FC750054902CEAF9DA090D82DCF39B85D`。Linux再配信と実機受入はR06/R07として残す。
- 2026-07-14にR06/R07を含む現行bundleをLinuxへ再配信し、Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、候補19 / decision 9 / execution link 4を確認した。Hub 1438×715の左レール・2列ダッシュボード、Tasksの左レール・主要tab・`マスタ管理`三セクションと追加導線はCodexが読み取り確認済みである。残りはユーザーが強制再読込後に行う見た目・操作感の最終受入だけとする。
- 同日に追加の非破壊読取り監査として、TasksのHome / Project Dashboard / List / Gantt / Table / Kanban / task detail / `マスタ管理` / 今後の予定の9画面を現行Linuxで開いた。全画面にmain要素と想定見出しがあり、`Vikunjaを読み込み中…`の残留とdocument-level横overflowはなかった。候補・task・設定の変更、画面の見た目・操作感の判定はしていない。

## P0追加タスクの完了条件

- 主要画面の全操作に、実行結果または明示的な読み取り専用理由がある。
- 「Tasks側を開く」「更新」「編集」「GO」などの主要ボタンを実画面で操作し、状態変化を確認できる。
- Hub編集対象とVikunja編集対象の境界が画面上で説明されている。
- 無効・未接続・空状態が、理由と次の操作を持つ。
- 最新DBフィールド、実データ、リンク、件数、ガント表示が一致する。
- 1280px / WQHD / 4K縦3分割相当の操作受入と、Hub/Vikunjaの回帰証跡が揃う。

## P1との関係

この追加タスクが完了するまで、P1の実機運用仕上げは開始ゲートを保留する。P0のバックエンド契約を作り直すのではなく、フロント受入と操作責務を完成させる。
