# ユーザーに次に答えてほしいこと

## P0フロント受入で必要な実画面準備

P1へは進めず、P0フロント受入を継続する。ユーザーが行う操作は、次のHTMLを上から順に実行するだけでよい。

- `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`

各行で完了または未達を選び、未達理由・見た目の違和感・作成した候補/task IDをコメントする。末尾の「報告プロンプトを生成」で出た内容をCodexチャットへ貼る。

1. HTML先頭のB01で、Hub / Tasks再配信、API 200、SQLite integrity `ok`、候補・判断・link・Task 0件のclean baselineが完了済みであることを確認する。追加操作はない。
2. B02で、HubチャットのLLM到達性をP0必須として回復するか、`degraded`の縮退受入とするかを決め、コメントへ記録する。
3. B03の関連行R06/R07、RV01〜RV05、U05を上から確認し、全て承認した後だけB03を完了にする。R06/R07の再配信操作は不要で、現在は最終見た目・操作感の確認だけを行う。
4. B04/U03とB05は実データを変更する。各行へ進む前にCodexへ確認し、B05は`実取込GO`がある場合だけ1batchをpending候補まで取り込む。どちらも自動GOや一括削除は行わない。

通常のHub / Tasks source-only再配信はCodexが専用SSH鍵で直接行うため、ユーザーはPowerShellやSSHを実行しない。sudo、鍵の初回登録、secret/env設定、実データ変更が必要な作業だけをユーザー境界とし、パスワード、env全文、secret、token、Cookie、秘密鍵は共有しない。

## 後続: Slack / Misskey定期worker有効化（今は実行しない）

Codexによるfake API / fake LLM回帰とsource-only実装は完了した。実token、実API、Linux env設定、実SQLite書込み、timer有効化は未実施であり、ユーザーがこの有効化を選ぶまで行わない。

実装完了後にCodexから依頼があった場合だけ、repo外のLinux envへ次を設定する。値はチャット、Git、ログへ貼らない。

- Slack: `memo-ideas`だけを読める内部bot app、`channels:history`、対象channelへのbot参加、`SLACK_OWNER_USER_ID`、初回取得境界`SLACK_INITIAL_OLDEST_TS`
- Misskey: 接続先origin、本人user ID、必要なvisibilityだけを読めるaccess token

設定後も、最初は`--commit`なしの手動dry-run 1回だけを実行する。件数と一般化errorを確認し、Codexが実データ変更を明示して再確認した後だけ手動commit 1回へ進み、timer有効化は候補品質の受入後に分離する。

## 現在のユーザー確認

Tasks本文にHub由来のオレンジが残る実機差分を確認した。R06でTasksのprimary/link/focus/選択行/left rail/button/card/task/dashboard/calendarをTasks青・淡青へ統一するsource修正を行い、R07でプロジェクト・ラベル・チームを`マスタ管理`へ統合した。2026-07-15時点のLinux実データは洗い替え済みで、候補0 / decision 0 / execution link 0 / Vikunja task 0、Tasks APIは利用可能である。P0を閉じるにはR05、R06/R07、RV01〜RV05、U03/U05の最終受入と、新しいVault AI batchの実データ品質確認が必要である。P1本実装はこれらの受入後に再開する。

次にユーザーが行うのは、受入HTML先頭のB02でHubチャットLLMを「P0必須として回復」または「degradedで縮退受入」のどちらにするか判断することである。その後はB03の関連行R06/R07、RV01〜RV05/U05へ進む。B04/U03とB05の実データ操作は、各実行前の確認後に行う。

### Windows knowledge-vault AI batchの実データ受入

設計・実装・自動回帰、`gemma4:latest`への合成入力、実Vault最新3文書のdry-runは完了した。dry-runは提案5件中3件をaccepted、根拠完全一致でない2件をheldにし、Linux転送・SQLite変更・候補登録・GOは行っていない。

最新HubはLinuxへ再配信済みで、新lineage table 5件はいずれも0行、既存候補・判断・link・Taskも0件のままである。次の実Vault batchを1回取り込む操作はpending候補とlineageを実データへ追加する。Codexは実行直前に確認を取り、実行後は候補の原文忠実度、固有名詞・path、actionの具体性、aspirationの希望表現保持、不要候補率を一覧で示す。ユーザーが見るのはHubの候補本文だけで、GOは別確認とする。

### 完成度レビュー（黄色枠・実データ変更なし）

実装済みだが十分な出来かを判断するため、受入HTMLの最上部にRV01〜RV05を追加した。`tmp/ui-review/p0-review-2026-07-12/`の黄色枠画像を上から開き、許容できる場合は完了、改善が必要または判断できない場合は未達を選ぶ。未達時は画面名・幅・気になる箇所・改善案をコメントし、最後に報告プロンプトを生成して貼り付ける。

再受入JPEG一覧はHTML内にbefore/afterのサムネイルとして表示される。サムネイルをクリックすると拡大表示になり、閉じるボタン・背景クリック・Escキーで一覧へ戻れる。

- RV01: Dashboardの処理状況、30日カレンダー、未日程/最近のタスク/ビューの密度
- RV02: Ganttのguide、日付範囲・時間軸、下部空白、初期導線
- RV03: Kanban 4列の同時認識、列幅、内部スクロール、下部空白
- RV04: task detailのタイトル/メタ情報、説明、コメント、操作面の読み順
- RV05: before/after証跡の画面高不一致（再撮影が必要か）

Thread Line画像とR03のALLOK部分は今回のレビュー対象に含めない。U03のGO/不要/アーカイブは実データ変更前に確認を取る。

### R03 Hub管理画面ブロッカー解除（ユーザーの対話SSH + Chrome）

1. Windows PowerShellで現行Hub bundleを転送する。

   ```powershell
   scp G:\devwork\pj-general\tmp\pj-general-web-working-tree.tgz unibell4@192.168.0.200:/tmp/
   ```

2. Linuxの対話SSH端末でhashが一致することだけ確認する。一致しない場合は以降を実行しない。

   ```bash
   EXPECTED=B9EB93B0ABEC1769C503AA6A3828A75BCC6A101F9809BE9720EF314922A7B7B9
   test "$(sha256sum /tmp/pj-general-web-working-tree.tgz | awk '{print $1}')" = "$EXPECTED"
   ```

3. hash一致後、Hub sourceを展開し、`pj-general` serviceだけを再build・再作成する。

   ```bash
   cd ~/pj-general-deploy
   sudo tar -xzf /tmp/pj-general-web-working-tree.tgz -C ~/pj-general-deploy
   cd ~/pj-general-deploy/infra/deploy
   sudo docker compose --env-file .env -f compose.yaml up -d --build --force-recreate --no-deps pj-general
   sudo docker compose --env-file .env -f compose.yaml ps
   for i in $(seq 1 15); do
     if curl -fsS http://192.168.0.200:4173/api/health; then break; fi
     sleep 2
   done
   curl -fsS -o /dev/null -w '%{http_code}\n' http://192.168.0.200:4173/api/bootstrap
   ```

   起動直後に最初のcurlだけが失敗する場合は、上の待受ループで復帰する。15回後も失敗する場合だけ、次の診断を行う。

   ```bash
   sudo docker inspect pj-general --format 'status={{.State.Status}} exit={{.State.ExitCode}} error={{.State.Error}} oom={{.State.OOMKilled}}'
   sudo docker logs --tail 80 pj-general 2>&1
   ```

4. ChromeでHub管理画面を再読込し、状態ラベルがタイトル横、`取込` と `有効化` / `無効化` が縦積み、入口設定・タグマスタ・プロンプトテンプレート・取込対象が先に読める2列配置であることを確認する。

R03ではVikunjaを再buildしない。DB/files/volume削除、再インポート、env全文表示は行わない。詳細な受入欄は `p0-frontend-acceptance-checklist-2026-07-12.html` のR03を使う。

### Thread Line Hub / Tasks共通識別・左レールブロッカー解除

2026-07-13に、正式な縮小版`thread-line-mark-master-256.png`をHubとTasks forkのsourceへ統合した。旧来のSVG生成・承認手順は不要であり、以下の旧手順は実行しない。Linux配信用bundleを更新した後、ユーザーが行うのはHub/Vikunjaを再buildして、左右レールに同じTLマークが44pxの直角フレームで表示されることを確認することだけである。原寸PNGはサーバーへ配信しない。

R05のPowerShell一行scriptによる再配信は完了した。ChromeでHub `http://192.168.0.200:4173/`とTasks `http://192.168.0.200:3456/`を強制再読込し、TLマークが44px正方形で途切れず、Hubは薄橙の`Thread Line Hub`、Tasksは薄青の`Thread Line Tasks`、Inboxにも青のアイコン、Kanbanにはguideがないことを確認する。問題がなければ受入HTMLのR05を完了にする。

### 廃止: SVG前提の旧手順

1. 別の画像・SVG実装セッションで `docs/product/thread-line-logo-handoff-2026-07-12/NEXT-SESSION-PROMPT.md` をそのまま実行する。
2. `assets/07-silver-white-glass-selected.png` と `VECTOR-SPEC.md` を視覚・数値の正本にし、master / Hub / Tasksの透明背景SVGを作成する。追加の画像案探索は行わない。
3. 1000 / 128 / 48 / 24px previewを確認し、SVG単体の見え方をユーザーが承認する。承認前にHub / Tasksへ組み込まない。
4. 承認後、CodexがHubとVikunja forkへ同じpath骨格のTLを実装し、二重スクエア識別、共通左レール、Hub薄橙／Tasks薄青の差分、1280/WQHD/4K縦3分割の回帰と配信bundleを更新する。

このThread Line手順ではLinux配信・Docker操作・実データ変更・再インポートを、SVG preview承認前には行わない。進捗は `p0-p1-completion-assessment-2026-07-12.html` のThread Line行へ反映する。

1. P1の最優先を `常設運用・観測 -> Vikunja fork配信 -> 定期入口worker` としてよいか。
2. Linux常設環境への接続・配信作業を開始できる時期。
3. Misskey / Calendar / 部分自動確定は、常設運用データを得た後のPoCでよいか。

P1の判断材料は `docs/product/p1-phase-brief-2026-07.md` を参照する。

## P0の履歴

P0の受入・実機作業は完了済み。以下は再検証時に使う履歴手順である。

次にユーザーが手を動かす想定は、P0 の実装画面をブラウザで触り、確認待ちキュー、書き入れ口、横断ダッシュボード、TODO主導線の体験を見て調整点を返すこと。

## 2026-07-11 Vikunja結合の実機確認結果

設計確認、Linuxサーバー準備、実Vikunjaへのtask作成、Webhook、再照合は完了した。現在はP0受入と、frontend fork dashboardのUI方針確認へ移っている。

1. `docs/imp/p0-status-audit-2026-07-11.md`でP0の完了・残件・判断事項を確認する。
2. Hubの実画面を確認し、P0受入またはUI微調整点を返す。
3. Vikunja frontend forkのdashboardをレビューする場合は、`docs/imp/current-goal-and-data-structure-brief-2026-07-11.md`を先に読む。

SQLite migration、実在Vikunjaへの作成、Webhook、再照合、実機画面確認は完了している。再起動・backup/restoreは運用継続時の保守確認として残す。

### 実機起動後の準備（完了）

1. [x] Linuxの`unibell4`へ、このWindowsのSSH公開鍵を登録する。
2. [x] Vikunja画面でruntime API tokenを発行し、サーバー上の権限600のenvへ保存する。

Vikunja `v2.3.0`のAPI応答は確認済み。project IDはAPI token取得後にCodexがAPIから特定するため、ユーザーが先に調べる必要はない。

### 2026-07-11 実機結合後の判断待ち

- [x] 専用Docker network内で`VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS=true`を有効化した。
- [x] 診断中に出力へ露出した`pj-general-integration`と`dev-codex-api`を削除し、`pj-general-runtime`だけを残した。

## 2026-07-09 確認してほしい箇所

- WQHD で横断ダッシュボードから TODO への主導線が、迷わず読める密度になっているか。
- 左側 1/4 程度に寄せた入口別・候補種類のサマリが、見やすいか。上部 1/3 型のほうが良いか。
- 上部の metric 8 個が多すぎないか。削るならどの指標を削るか。
- ガント補助表示を残す場合、週メモリ、タスク名、担当、進捗、バー位置が読み取りやすいか。
- 確認待ちキューの詳細 pane で `GO` / `編集` / `不要` / `アーカイブ` が折り返されず、判断しやすいか。
- 右 drawer の書き入れ口が、常時呼び出せる入力口として重すぎないか。

## 2026-07-10 反映済みフィードバック

- 横断ダッシュボードは、ピクセルパーフェクトではなく配置優先で高密度化する。
- 入口別の量、候補の種類などのサマリは、左側 1/4 程度に圧縮する方向を第一候補にする。
- 文字サイズは小さくしすぎず、読める大きさを保つ。
- 確認待ちキューは現状の方向で進め、詳細 pane のタイトルと本文に色・濃淡差をつける。
- 管理画面の最小範囲は、P0 完了時の機能がそろって見える状態まで作る。
- 今のブルーをベースに、操作可能、選択中、操作不能を明暗・濃淡で区別する。
- 不要な角丸は減らす。
- 次フェーズは、mock ではなく SQLite 永続化と実入口を備えた P0 本デモ化を目指す。

## 2026-07-10 P0 本デモレビュー手順

当時の確認URL:

```text
http://127.0.0.1:4173
http://127.0.0.1:4173/chat
```

確認してほしい順番:

1. 横断ダッシュボードで候補数、入口別、種類別、優先確認、Vikunja TODO への主導線が見えるか確認する。
2. 右下の `書き入れ` から候補を追加し、リロード後も確認待ちキューに残るか確認する。
3. 確認待ちキューで候補を選び、詳細 pane の `編集` から title / summary / todo / schedule / tags を編集して保存する。
4. `保存してGO`、`GO`、`不要`、`アーカイブ` の状態遷移が自然か確認する。
5. 管理画面で source / prompt template の有効状態を切り替えられるか確認する。
6. 管理画面の knowledge-vault `取り込み` を押し、imported / skipped / scanned の結果表示を見る。
7. Slack `memo-ideas` は現時点で取り込み対象投稿がないため、`同期確認` で imported 0 の表示を見る。

## 2026-07-11 ローカルLLM相談窓口の確認

1. `/chat` で相談を送り、回答本文と会話履歴が表示されるか確認する。
2. 回答にタスク候補が出た場合、`候補として追加` を押して確認待ちキューへ追加されるか確認する。
3. 通常画面で `相談` または上部の `C` を押し、TODO・予定を見ながらサイドウィンドウで同じ履歴を続けられるか確認する。
4. `/chat` とサイドウィンドウを往復し、候補の追加済み状態が共有されるか確認する。
5. Ollamaを停止した状態で、既存Hub画面が壊れず、相談欄に接続エラーが表示されるか確認する。

## 2026-07-12 ローカルLLMエージェント相談窓口の受入

今回の要件は既存の相談窓口 v1 に統合済み。以下を確認する。

1. `/chat` で、現在のHub候補・Vikunja Tasks概要を踏まえた回答が返るか確認する。
2. 「今のタスク状況を見て」のような相談で、agentの読み取り専用context参照が回答に反映されるか確認する。
3. タスクらしい相談で候補が表示され、`候補として追加` の1操作で確認待ちキューへpending登録されるか確認する。
4. 通常Hubの画面で、TODO・予定を見ながら `相談` のサイドウィンドウを開き、同じ会話を継続できるか確認する。
5. ローカルLLM停止時に、既存Hub・確認待ちキュー・Vikunja導線が壊れないか確認する。

実装済みの境界:

- agent toolは読み取り専用で、`all` / `tasks` / `candidates` のscopeを持つ。
- タスク作成は既存 `candidates` へのpending登録だけで、LLMは直接登録・GOしない。
- pending後は既存の確認待ちキュー、GO、Vikunja連携を使う。

## 2026-07-12 継続監査の確認

- WQHD撮影結果: `tmp/current-hub-wqhd-full.png`
- 固定Gantt除去後のフルスクロールWQHD撮影結果: `tmp/current-hub-dynamic-gantt-full.png`
- AI相談画面: `tmp/current-hub-chat-wqhd.png`
- 通常ダッシュボードからAI相談の埋め込み空白を除去し、`/chat` とサイドウィンドウへ分離した。ここは変更方針に異論がないか確認する。
- Vikunja fork dashboardの確認URLは、Linux custom imageを起動できるまで未提示。実機起動後に、30日カレンダー、未日付一覧、既存List / Table / Kanban / Gantt導線を確認する。

判断してほしい点:

- SQLite ローカル永続化をP0の基盤としてこのまま進めてよいか。
- 確認待ち詳細の編集項目は、P0として過不足ないか。
- 管理画面のP0最小範囲は、レビュー前として十分か。
- knowledge-vault import の対象を増減する必要があるか。
- Slack `memo-ideas` に実投稿を入れた後、Codex connector 経由 import をP0運用にしてよいか。

## 2026-07-10 SQLite完結版の追加確認

1. 横断ダッシュボードで、数値8件がなくなり、左に入口別量・候補の種類、右に処理フロー、優先確認、判断ログが縦に並ぶか確認する。
2. 確認待ちキューで、詳細 pane が左・一覧が右になっているか確認する。
3. 作業者用の `コピー` を複数回押し、毎回 Codex 起動支援テキストがクリップボードへ入るか確認する。
4. 管理画面で、タグの追加・表示切替、ロール・AI方針・取り込み対象・source・prompt の有効切替を行い、リロード後も状態が残るか確認する。
5. knowledge-vault の対象を一つ停止して `取り込み` を実行し、停止対象がスキャンされないか確認する。
6. Slack は実メッセージを connector から取得した JSON 配列だけを `Slack memo-ideas payload` へ入れて取り込む。空データを擬似送信する動作はない。

## 2026-07-11 Hub / Tasks結合の確認

1. 横断ダッシュボードの `Tasks側の概要` で、Vikunjaの全タスク数、未完了、完了、直近タスクが表示されるか確認する。
2. `Tasks側を開く`、確認待ち詳細のTasks側リンク、参考ガントのTasks側リンクからVikunjaへ遷移できるか確認する。
3. HubでGOした候補がTasks側へ登録され、登録後はTasks側で期限・担当・進捗・完了を操作する一方向の流れでよいか確認する。
4. Hubへ戻ったとき、Webhookまたは再照合で実行状態だけが表示へ反映され、候補本文や判断が勝手に書き換わらないことを確認する。
5. データ・導線の確認後、`docs/imp/p0-frontend-completion-tasks-2026-07-12.md` のHub / Vikunjaフロント受入へ進む。

## 2026-07-12 Listening Lounge 本流化後の確認

ユーザー判断により、4案のうち `Listening Lounge` を本流へ昇格した。

確認URL:

```text
http://127.0.0.1:4173/
```

確認する点:

1. 通常URLを開いた時点で、夜、藍、銅、音響パネルのListening Loungeが表示されることを確認する。
2. 上部に比較用 `Room studies` が残らず、業務画面として自然に始まることを確認する。
3. 確認待ち、書き入れ、AI相談、管理、Tasks側導線を触り、操作状態の区別に問題がないか確認する。
4. 縦分割相当の横幅でも、入口別の量と候補の種類の下端が揃い、文書全体の横スクロールがないことを確認する。
5. 今後伸ばしたい要素を、照明、壁面パターン、銅色の強さ、情報密度、タイポグラフィの観点で返す。

本流は実SQLite/APIへ接続しているため、`GO`、`不要`、管理設定変更は実データを更新する。

## 2026-07-12 Vikunja Listening Lounge 実画面監査

- [x] Chromeで `http://127.0.0.1:4176/login` を開き、既存Vikunjaアカウントで一度ログインする。
- [x] ログイン後にCodexへ「ログインした」と伝える。

ログイン後はCodexが、認証済みhome / dashboard / list / sort / filter / task detailを1280pxと1920pxで操作・撮影し、`tmp/ui-review/vikunja-listening-lounge/after/` へ保存する。パスワード、Cookie、localStorageはCodexから読み取らない。
