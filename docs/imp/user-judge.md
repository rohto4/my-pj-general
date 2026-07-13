# ユーザー判断待ち

## 判断済み

- Google Calendarの「ユーザーGOで登録する」原則は維持する。実装時期は現行P0からP1後半PoCへ変更し、双方向同期は含めない。
- 外部協力者に最初から見せる情報は、スケジュールを中心にする。
- `UJ-VIKUNJA-01`: 実行の主導線は Vikunja の TODO を優先候補にする。初期は upstream 無改変の自己ホスト、`GO -> Vikunja task作成` の一方向 API 連携、Webhook受信で検証する。backend plugin で済む拡張を先に検討し、TODO画面の変更が必要な時だけ fork を判断する。ガントは TODO の副次ビューとして必要な時だけ開く。
- MVP にキャパ管理は入れない。
- Codex プロジェクト起動支援は、スケジュールページではなく、作業者用 / タスクサマリページをトリガーページにする。
- 4 つの窓口ごとの表示内容と操作範囲は定義済みとして扱う。
- `UJ-01`: Slack / knowledge-vault から回収する対象範囲は、Slack は `memo-ideas` チャンネル、knowledge-vault は diary 系、`records/`、`inbox/`、記憶層 L1-L2、legacy `tasks/active/`、`tasks/handoff/` を参照対象にする。対象内容は、やりたいこと、困っていること、タスクっぽいこと。knowledge-vault は対象範囲内をいったん全件対象にする。
- `UJ-02`: P0ではすべての候補を確認待ちにする。部分自動確定はP1で判断実績とdry-runを得てから再判断する。
- `UJ-03`: 確認待ちキューの表示項目と GO 操作は Codex に一任し、実画面を触ってから調整する。
- 4つのテーマ案から `Listening Lounge` をHub本流へ採用し、Vikunja frontend forkも同テーマへ統一する。
- P0のバックエンド・連携契約は正式完了とする。フロント受入と編集責務の確認は追加P0で扱う。
- `UJ-THREAD-LINE-01`: TLモノグラムは`assets/08-satin-gradient-selected.png`を最終選定する。正式配信物は同一内容の`thread-line-mark-master.png`と、その高品質縮小版`thread-line-mark-master-256.png`とする。SVGは使用しない。

## 判断待ち

- `UJ-P0-FRONT-01`: Tasks概要・ガント・Vikunja task detailをHubから直接編集するか、Vikunja側編集の読み取り導線として固定するか。
- `UJ-P0-FRONT-02`: 画面上の全ボタンを実操作として提供するか、読み取り専用箇所は説明付きの非操作表示にするか。
- P0フロント受入追加タスクの実画面確認待ち。
- P1開始時に、優先順、Linux配信時期、後半PoCの順序を確認する。

## P1開始時に確認する事項

- Vikunja frontend dashboardを常設環境の標準ビュー入口にするか。
- 既定の「今日から30日」と日付なしtask一覧をP1運用でも維持するか。
- Hubに残すTasks概要の情報量と、Tasks側へ寄せる表示範囲。
- Misskey実接続、AI部分自動確定、Calendarを常設運用データ取得後のPoCとするか。
- ローカルLLM相談の書込み境界は、候補提案までに維持する。

## 現時点の仮説

- MVP は「アイデアカード -> タスク化 -> 予定化」の一気通貫が中心
- ガントは TODO の副次ビューにする
- キャパ管理は MVP から外す
- ロール管理は MVP 必須
- Codex プロジェクト起動支援は、タスクサマリから起動する導線が自然
- 候補は全件確認待ちで見せ、部分自動確定条件はP1の実運用データで再設計する

## 方針更新

- ユーザーは現時点で実装順より要件整理の深さを優先している
- 以後の質問は、MVP に絞り込むためだけでなく、将来要件も含めて広めに拾う
