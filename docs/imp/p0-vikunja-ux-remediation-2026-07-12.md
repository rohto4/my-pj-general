# P0追加: Vikunja全画面UX再改修・証跡

## 目的

Listening Lounge forkの実機画面を、1280px、WQHD、4K縦3分割相当で再受入する。task detailで要素が散らばる問題、Gantt初回遷移の表示不良、各画面の操作感を改修する。

## 採用した導線方針（2026-07-12）

- Vikunjaを単独で開いた時の初期遷移先をInbox Dashboardへ固定しない。複数Projectを前提に、`/projects` のProject一覧を既定入口とする。
- HubからTasks側へ遷移する場合は、execution linkが持つVikunja Project / task URLを優先し、対象ProjectのDashboardまたは対象taskへ直接遷移する。
- 左メニューの標準`概要`・`今後の予定`はP0導線から外す。Projectを選択した後は、Dashboard / List / Gantt / Table / KanbanをProjectのサブリストとして主導線にする。
- Project・Label・Teamの追加/一覧は単一の管理入口へ統合する。ただし既存route/APIは削除せず、旧URLから管理入口の該当セクションへ誘導する。

## 対象画面

1. Login
2. Home
3. Project Dashboard
4. Inbox
5. List
6. Table
7. Kanban
8. Gantt
9. task detail

## 必須証跡

- 各画面について、変更前・変更後の**全画面**JPEGを保存する。
- 保存先: `tmp/ui-review/vikunja-listening-lounge/reacceptance/`。
- 命名: `<tab>-<function><No>-before.jpg` / `<tab>-<function><No>-after.jpg`。
  - 例: `task-detail-layout01-before.jpg`、`task-detail-layout01-after.jpg`。
- 各画像と対応する表示幅・操作・判定を同フォルダの`README.md`に追記する。
- 既存PNGは過去証跡として保持し、今回の再受入JPEGを置換正本とする。

## 改修順

1. 認証済みブラウザで現行forkを開き、対象9画面のbefore JPEGを撮影する。
2. task detailを4K縦3分割相当で、編集面・操作rail・本文・サイド情報が視線を分断しないよう再構成する。
3. Ganttは初回router遷移時にtimelineが確実にlayoutされるよう、view mount / data load / animation frame後に再計測する。二度クリックを利用者へ要求しない。
4. Home / Dashboard / Inbox / List / Table / Kanban / Gantt / task detailのguide、empty、primary actionを一画面ずつ確認し、同じListening Lounge token・情報密度・square surfaceへ整える。
5. 1280 / WQHD / 4K縦3分割でafter JPEGを撮影する。document-level横overflow、画面外へ逃げる主操作、過剰な空白を確認する。
6. frontend unit / stylelint / production buildを実行し、実機URLで再受入する。

## ユーザー操作が必要な時だけ

- Vikunjaログインはユーザーが行う。パスワード、Cookie、tokenは共有しない。
- 実在taskを変更する必要がある場合は、変更前に確認する。画面閲覧・layout確認・スクリーンショットだけでは変更しない。

## 現在の判定

- Login画面のListening Lounge themeは実機確認済み。
- 2026-07-12にユーザーがChromeでVikunjaへログイン済み。認証待ちは解除した。
- Homeの現行before画面は、青いVikunja専用identity headerがHubとの主要差分であることを実機確認した。
- fork sourceへ第一段階を反映済み: 青い`Vikunja / Tasks workspace` identity headerと固有タイトルは維持し、その下をHubの横幅208px、書体、余白、罫線、銅線、藍の選択行、hover時5px横移動へ統一した。
- task detailは4K縦3分割相当（幅1440px以下）で本文と操作railを縦に分け、操作を2列面に再構成するresponsive layoutを追加した。
- fork固有unit test 12件、変更6ファイルのstylelint、production buildをWindowsで再成功させた。Ganttは初回router遷移後の二重animation frame・ResizeObserver・tab復帰に加え、行・日付軸DOM生成後にも再計測する。Kanbanは追加バケットを含めて4列grid、Dashboardは処理状況を低背横並びにし、カレンダー・未日付タスクを直後へ表示する。`pnpm`経由ではJunctionの依存削除確認が出るため、既存node_modulesを削除・再installせず、リンク先の実行fileをNode 24 runtimeで直接実行して検証した。上流Sassの`@import`非推奨とWorkbox更新確認の権限警告は出るが、production buildの終了状態は成功である。
- 更新bundle `tmp/vikunja-listening-lounge-working-tree.tgz`を、対象6ファイルを展開比較して現行sourceと一致確認後に作成した（SHA-256: `E90236D8AED9CB90077270D968EF82AC085B8997D2C7EAD2FDB81D9085CD544F`）。Linuxではsource展開後に`./start-pj-general.sh --start --rebuild-vikunja`でimageを再buildする。
- E902…544FをLinuxのListening Lounge custom imageへ再buildした。起動直後の4173接続失敗はcontainer起動前だけの一時状態で、その直後のHub healthとVikunja APIは正常だった。Chromeの1280px task detailで右操作railが本文下の操作面へ移ることを確認し、V01を完了とする。再インポート、DB/files/volume削除はしていない。
- 2026-07-12にChromeでDashboard / Gantt / Kanban / task detail / List / Table / sidebarを9条件で再巡回し、`tmp/ui-review/vikunja-listening-lounge/reacceptance/`へbefore/after JPEGを保存した。WQHD（01/02/03）、1280px（05/06/07/09）、4K縦3分割相当1440px（04/08）のいずれもdocument横overflowは検出されなかった。
- fork frontend unitは51 files / 1086 testsが成功し、Listening Lounge固有のテーマ・Gantt初回layout・Kanban 4列・Dashboard順序・task detail狭幅ルールも回帰確認済み。Sass `@import`非推奨警告とVue Test Utilsの未登録component warningは既存 upstream由来で、テスト終了状態は成功である。
- **未完了**: RV01〜RV05/U01/U05の具体的な画面改善と、ユーザーによる再受入。RV01はPROJECT OVERVIEW/VIEWS削除・PJ名表記・日付未定タスク整理、RV02は前2週〜向こう2か月・日付変更確認・完了バーの灰色化、RV03はguide削除・無制限縦高、RV04はタイトル/パンくず順・狭幅右操作・文字サイズ、RV05は1438x715同一条件のbefore/afterへ分解した。agentはtaskの編集・完了・期限・担当変更をしていない。
- Tasks左レールのアイコンはHubと同じ記号/輪郭/24px枠を使い、Hubは銅オレンジ、Tasksは青へ変更するfork source修正を追加済み。配信と実機確認は未完了。
