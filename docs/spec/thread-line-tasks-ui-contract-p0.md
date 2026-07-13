# P0 Thread Line Tasks UI契約

## 目的

Vikunja frontend forkにおける`Thread Line Tasks`のP0画面、操作、表示責務を定義する。Hubと共通の左レール・ブランド要件は `docs/product/thread-line-workspace-requirements.md`、Hub / Vikunjaの連携境界は `docs/spec/vikunja-integration-contract-2026-07.md` を正本とする。

## 入口と画面責務

- Tasksを直接開き、対象Projectまたはtaskが特定できない場合はProject一覧を表示する。
- Hubから対象Projectまたはtaskが特定できる場合は、Project Dashboardまたはtask detailを直接開く。
- Projectを選んだ後の主導線はDashboard、List、Gantt、Table、Kanbanである。標準の概要・今後の予定はP0主導線から外す。
- Project、Label、Teamは左レールで個別に並べず、`マスタ管理`へ統合する。既存の個別URLと作成・編集フォームは互換性のため維持する。
- Hubは入口、候補、判断、GO、連携状態を編集し、Tasksはtaskのtitle、期限、担当、進捗、完了を編集する。TasksでHub候補本文・判断を逆編集しない。

## 左レール

- 識別領域は`Thread Line Tasks`だけを表示し、旧`Vikunja`と`Tasks workspace`の副題を表示しない。
- TLマークは44px × 44pxの直角フレームで配置する。Tasks側の輪郭とアイコンはTasks青、寸法、罫線、藍色offset、行高、hover時の横移動量はHubと同一にする。
- 識別領域は飽和した青で塗りつぶさず、薄青`#29385b`とインク・細い罫線で構成する。
- menuのaccentはTasks青`#5176d8`と淡青`#89b8ff`だけを使う。本文の操作、link、focus、選択行、rail、calendar、timeline、guideにHub固有の銅オレンジを使わない。
- 個別Project行には、24px占有幅でTasks青のアウトライン記号を置く。

## Project Dashboard

表示順は以下とする。

1. `<PJ名>のタスク概要`。PJ名を主、説明語を薄い補助文字にする。
2. 処理状況。全task、未完了、完了、期限超過、今後30日の数字を低背の横並びで、利用可能幅の左半分までに置く。
3. 今後30日のカレンダー。
4. 日付未定タスク。完了taskを含めない。

- `PROJECT OVERVIEW` guideと`VIEWS` blockは表示しない。
- Dashboardはタスクの実データを表示し、空、読込、失敗時に意味と次の操作を示す。
- 編集はList、Table、Kanban、Gantt、task detailの既存ビューで行う。

## Gantt

- 初回router遷移でも、日付見出し、行、barを正しく計測・表示する。利用者へタブ切替や二度遷移を要求しない。
- 既定範囲は前14日から向こう62日とする。
- barのdragまたはresizeが日付変更を発生させる前に、変更内容を確認する。拒否時は表示、task、APIのいずれも変更前へ戻す。
- 完了barは未完了barより明確に灰色化し、読み取り優先度を下げる。
- 日付なしtask、期間外task、0件では、意味、作成または表示切替、戻り先を表示する。

## Kanban

- 4列を含む全bucketを省略しない。
- 幅不足時はKanban面だけを横スクロール可能にし、document-levelの横overflowを発生させない。
- `KANBAN VIEW` guideを表示しない。
- 列内の縦高は固定せず、taskを内部縦scrollへ隠さない。ページ側の縦scrollで読める状態にする。
- bucket 0件では、空である意味、task追加、戻り先またはfilter解除を示す。

## Task detail

- breadcrumbをtitleより前に置く。
- 4K縦3分割相当でも、完了、購読、その他の主要操作を右側の操作面に残す。
- 説明とコメントはAI相談画面相当の小さな文字密度にし、本文、metadata、操作の読み順を分断しない。
- 編集・完了・期限・担当・進捗の変更はTasksで確定し、Hubには実行状態のmirrorだけを返す。

## guide / empty / action

- Home、Dashboard、Inbox、List、Table、Kanban、Gantt、task detailは、入力、画面で起きる変化、次の一手をguideとして示す。
- task 0件、bucket 0件、日付なし、filter 0件、未接続または取得失敗では、固定sampleを出さず、意味、主操作、代替ビューまたは戻り先を示す。
- guideは画面の主要操作を妨げない。DashboardのPROJECT OVERVIEW、KanbanのKANBAN VIEWのように重複するguideは表示しない。

## 幅別受入と実装境界

- Login、Home、Project Dashboard、Inbox、List、Table、Kanban、Gantt、task detailを1280px、WQHD、4K縦3分割相当で受入する。
- document-level横overflowは許可しない。局所面だけを横scrollにできる。
- before/after JPEGは`tmp/ui-review/vikunja-listening-lounge/reacceptance/`へ`<tab>-<function><No>-before.jpg`と`after.jpg`で保存し、同一の1438x715・同一scroll位置で比較する。
- 実データ変更を伴うtask編集・完了・期限・担当操作は、操作前に利用者確認を得る。
- 実装を読む必要がある場合だけ、`tmp/vikunja-listening-lounge/frontend/src`の対象view、component、SCSS、対応unit testを読む。fork全体を先に読まない。
- 進行・実機受入は `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`、改修タスクは `docs/imp/p0-vikunja-ux-remediation-2026-07-12.md` を参照する。
