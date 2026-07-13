# Thread Line Workspace 要件

## 目的

`Thread Line Hub` と `Thread Line Tasks` は、同じ個人・チーム運用空間を構成する二つのアプリケーションとして、共通の情報密度、機械的な左レール、明確な編集責務を持つ。

## 1. 製品アイデンティティ

- Hubの左レール識別名は **Thread Line Hub** とする。
- Tasksの左レール識別名は **Thread Line Tasks** とする。
- どちらのアプリも、左レールの識別領域に二枚の正方形を斜めにずらしたマークを置く。
- 奥側の正方形はHubを表す薄い銅・オレンジ、手前側の正方形はTasksを表す薄い青とする。
- 二枚の正方形は装飾ではなく、HubとTasksが別の責務を持ちつつ同じ運用空間を構成することを示すブランド記号とする。
- HubとTasksは同じTLモノグラムの骨格を使う。masterはVikunja blueのT、Thread orangeのL、銀白ホワイトグラスのorbitとする。HubはivoryのT・copper orangeのL、TasksはVikunja blueのT・ivoryのLへ文脈配色を切り替える。
- TLモノグラムは画像アセットとして配信し、代替テキストを`TL`とする。画像未読込時にも製品名が可読でなければならない。
- 正式TLアセットは、縦長のセリフ系TとLを明確に分離し、左下の細い書き出しから右側・下側の太い帯へ遷移する斜めorbitを重ねる。正式配信物は原寸PNGと高品質縮小PNGとし、SVGへ描き直さない。視覚基準と画像実体は`thread-line-logo-handoff-2026-07-12/`を正本にする。
- サイトに実装するファイルは`thread-line-logo-handoff-2026-07-12/assets/thread-line-mark-master-256.png`とする。原寸の`thread-line-mark-master.png`は制作・保管用であり、サイト配信には使わない。
- HubとTasksの左レールは、この256px PNGを44px × 44pxの直角フレームへ`object-fit: cover`で配置する。Hubは銅の輪郭、TasksはTasks青の輪郭とし、両者のフレーム寸法、1px罫線、6pxの藍色オフセット、余白は共通にする。
- Tasks識別領域は飽和した青い面にせず、Hubのインク・ウールグレー・細い罫線・直角を基調とした薄青 `#29385b` の面にする。
- Tasks本文のブランドアクセントは、主要ボタン、link、focus、選択行、hover、左端線、card/task/dashboardのrail、カレンダー上端、timeline、guideの区切りを含めてTasks青 `#5176d8` と淡青 `#89b8ff` に統一する。銅オレンジはHub固有のアクセントであり、Tasks本文のテーマ色として使わない。
- Hub識別領域は薄橙 `#3d302d` の面に`Thread Line Hub`だけを表示し、旧`pj-general`と`P0 試作`の副題を表示しない。Tasks識別領域は`Thread Line Tasks`だけを表示し、旧`Vikunja`と`Tasks workspace`の副題を表示しない。
- 上部のVikunja既存ナビゲーションは、Vikunjaのアカウント操作・検索など既存機能を維持する。左レールの製品識別でHub/Tasksの役割を示す。

## 2. 共通の左レール

- 左レールの幅、メニュー文字、罫線、行高、hover時の横移動量はHubとTasksで揃える。
- 左レールのメニューアイコンは、記号の輪郭、24pxの占有幅、行高、左揃え位置をHubとTasksで完全に揃える。Hubのアイコン色は銅オレンジ、Tasksのアイコン色はTasks青とし、色以外の形状・余白・hover時の移動量は共通とする。
- Hubの主メニューは、上から **ダッシュボード / 簡易日程 / タスクキュー / ワークビュー / 簡易管理** の5項目だけとする。各項目は同名のHub内スクロール先へ移動する。
- Hub左レールの各項目は同一ページの `#dashboard` / `#gantt` / `#queue` / `#worker` / `#admin` へ遷移する。ハッシュ遷移と画面内ボタン遷移は同じscroll処理を使い、各セクションのscroll marginを尊重して見出しを同じ位置へ揃える。
- Hubの通常メニューから「相談」を除き、AI相談は左レール下部の独立したサイド操作として残す。
- Hubの左レール下部には、AI相談と同じボタン骨格で未実装・非活性の **詳細管理** を置く。詳細管理は操作できない理由として「準備中」を表示し、誤操作で状態を変更しない。
- メニューは直角の面、細い横罫、左端のアクセント線で構成する。丸角のカード群にはしない。
- hoverと選択状態では、Hubは銅、TasksはTasks青の左端線と、共通の藍色の面、文字の小さな横移動を使い、押下可能であることを明確にする。
- HubとTasksの識別領域を除き、TasksのメニューはHub側の機械的な密度と読み順へ寄せる。
- Tasksの個別Project行（例: Inbox）には、共通の24px占有幅でTasks青のアウトライン記号を必ず置く。
- Tasksのプロジェクト、ラベル、チームは左レールで個別に並べず、`マスタ管理`を単一入口とする。`マスタ管理`は10文字以内の短い名称で、プロジェクト・ラベル・チームの登録と確認を同一画面の3セクションで行う。
- `マスタ管理`からの追加操作は既存のProject／Label／Team作成フォームを使い、既存の個別URLは直接リンク・編集画面との互換性のため維持する。
- 左レールに置く主導線は、現在のプロジェクトに対するDashboard、List、Gantt、Table、Kanbanである。
- 標準の概要と今後の予定はP0の主導線から外し、必要なら統合管理面から到達可能にする。
- Hubから遷移先Projectまたはtaskが確定している場合は、そのTasks Project Dashboardまたはtaskへ直接遷移する。直接起動など遷移先が確定しない場合はTasksのProject一覧を表示する。

## 3. Hubの画面要件

- Hubは入口、候補、判断、GO、連携状態の正本である。Tasksのtitle、期限、担当、進捗、完了はTasksで編集することを画面に明示する。
- `Tasks側を開く`はTasksの主導線として強調し、Tasks固有の青を主要ボタン色に使う。
- 入口別の量と候補の種類は、他列の判断ログの高さに引き伸ばされない固定縦幅の反復リストとする。
- 処理フロー、Tasks概要、優先確認、判断ログは実データを表示し、空・読込・失敗・正常の状態と次の操作を持つ。
- デバッグ専用の表示、SQLite状態、運用観測、P0ルールは、通常の操作面と混同しない薄いオレンジ背景・銅の左罫線で統一する。
- Hub管理の状態カードは、`有効`または`停止中`ラベルをタイトル横に置く。
- 有効な設定は`有効`ラベルと`無効化`操作を、停止中の設定は`停止中`ラベルと`有効化`操作を表示する。
- 取込可能な設定は操作名を`取込`とし、`無効化`または`有効化`と縦積みにする。
- 4K縦3分割相当を含む狭い幅では、入口設定、タグマスタ、プロンプトテンプレート、取り込み対象を優先した2列配置とし、ロール表示とAI確定方針を後段の行へ置く。

## 4. Tasksの画面要件

- Project Dashboardは、プロジェクトの処理状況、直近のタスク、今後30日のカレンダー、未日程タスク、既存ビューへの導線を上から順に表示する。
- 処理状況は横並びの要約で縦余白を抑え、次に今後30日のカレンダーと未日程タスクを置く。
- Project Dashboardでは、重複する`PROJECT OVERVIEW` guideと`VIEWS` blockを表示しない。見出しは`<PJ名>のタスク概要`とし、PJ名を主、説明語を薄い補助文字とする。処理状況は利用可能幅の左半分までに留め、`日付未定タスク`には完了taskを含めない。
- Kanbanは狭い幅でも全バケットを省略しない。表示幅が不足する場合はカンバン面だけを横スクロール可能にし、文書全体は横overflowさせない。
- Kanbanでは`KANBAN VIEW` guideを表示せず、列内の縦高を固定しない。列内のtaskは内部縦scrollへ隠さず、文書側の縦scrollで読めるようにする。
- Ganttは初回遷移でも日付見出しと行が崩れず表示される。初期描画の計測・再計算が必要な場合は、利用者にタブ再遷移を要求せず内部で完結する。既定範囲は前14日から向こう62日とし、barをdrag/resizeして日付を変更する前には確認し、拒否時はtask/APIを変更しない。完了barは未完了barより明確に灰色へ退かせる。
- task detailは4K縦3分割相当で、本文と主要操作が一続きの読み順になる。breadcrumbをtitleの前に置き、主要操作は右側に残す。説明とコメントはAI相談画面相当の小さな文字密度にする。
- Home、Dashboard、Inbox、List、Table、Kanban、Gantt、task detailは、入力、画面で起きる変化、次の一手をguideとして示す。
- task 0件、bucket 0件、日付なし、filter 0件などのempty状態は、意味、作成操作、代替ビューまたは戻り先を示す。

## 5. P1開始後のProject連携要件

この節の複数Project連携はP0のフロント受入完了条件には含めず、P1開始ゲートを満たしてから実装する。P0では単一の個人Projectを既定の運用対象とする。

- Hubは複数Projectを扱い、個人Projectを既定表示できる。
- Hubで個別Projectを作成した場合、対応するTasks Projectを冪等に作成・対応付ける。
- 候補はHub Projectに所属し、GO時のTasks Projectは対応表から解決する。
- Project作成・対応付け・GO先解決・同期失敗は、候補判断と別の連携状態として表示し、再試行可能にする。
- HubからTasksへ候補本文や判断を逆同期せず、TasksからHubへ戻すのは実行状態のミラーに限定する。

## 6. 受入要件

- HubとTasksの主要画面は1280px、WQHD、4K縦3分割相当で受入する。
- 各幅でdocument-levelの横overflowを許可しない。必要な横スクロールはKanbanやtableなど局所面に限定する。
- 実データを使い、Hubの候補、判断ログ、Tasksの件数・直近task・担当・進捗・完了状態を受入する。
- UI改修は前後JPEG、回帰テスト、production build、Linux配信bundle、実機確認を同一の受入断面として残す。
- 実データを変更する候補作成、GO、不要、アーカイブ、設定変更は、操作前に利用者の確認を得る。

## 正本と同期先

- この文書は画面・体験・ブランドの確定要件の正本とする。
- 実装タスクとブロッカーは`docs/imp/imp-tasks.md`、ユーザー実機操作は`docs/imp/user-tasks.md`、受入の星取表は`docs/imp/p0-p1-completion-assessment-2026-07-12.html`に置く。
- Hub/Tasks間のデータ責務とAPI境界は`docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`と`docs/imp/p0-multi-project-linkage-design-2026-07-12.md`を参照する。
- Hub画面のhash遷移・状態・操作契約は`docs/spec/hub-ui-interaction-contract-p0.md`、Tasks画面のview別UI契約は`docs/spec/thread-line-tasks-ui-contract-p0.md`を参照する。
- 複数Projectの利用者導線、field、API、構成は`docs/product/multi-project-workspace-flow.md`、`docs/data/hub-project-linkage-data-design.md`、`docs/spec/multi-project-linkage-contract.md`、`docs/arch/hub-vikunja-multi-project-architecture.md`を参照する。
