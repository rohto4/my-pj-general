# ローカルLLM相談窓口 要件 2026-07

作成日: 2026-07-11

## 目的

通常のWeb / Slack / knowledge-vault入口とは別に、ユーザーがローカルLLMへ相談し、その直近の発言から具体的な作業と未確定の「やりたいこと」をHub候補として取り込める窓口を作る。

相談窓口は「LLMの回答画面」だけではなく、現在のHub候補とTasks側の実行状況を踏まえて相談できる作業入口とする。

## 利用形態

### 独立画面

- Hubのナビゲーションから `相談` (`/chat`) を選ぶ。
- 会話履歴、送信欄、現在のタスク状況、タスク候補カードを1画面で確認できる。
- 画面を離れても会話と候補状態はSQLiteに残る。
- 会話を主領域にし、現在contextは横一列の補助情報として表示する。
- 接続状態、会話数、thread IDは会話上部の1行へまとめ、provider / modelはlive contextへ表示する。
- 独立画面では説明用の大見出しと反復的な3段階フローに画面高を使わず、live contextの直後から会話を表示する。
- 送信欄は初期表示の画面内に置き、送信ボタンを入力欄と同じ行へ配置する。
- viewport高900px以下ではAI相談内だけ文字、余白、入力欄を縮小し、650px以下ではもう一段圧縮する。サイドメニューと通常画面の文字サイズは変えない。
- 短い発言を極端に細い吹き出しへせず、ユーザー / LLMの発言を読みやすい幅で分離する。
- 空の会話では無表示にせず、相談の役割と書き出し例を操作できる状態で表示する。

### サイドウィンドウ

- ダッシュボード、確認待ちキュー、作業者用画面を見ながら開ける。
- 左サイドメニューに常設した `AI相談 / サイドで開く` から、どのHub画面でも起動できる。
- 背景の予定・TODO表を維持したまま相談できる。
- 独立画面と同じthread、履歴、候補操作を共有する。

## 相談時にLLMへ渡す情報

Hub backendが毎回現在値を取得し、system contextとして渡す。

- Hubの候補: ID、タイトル、状態、種類、入口、信頼度、不足項目、予定案。
- Hubの実行リンク: candidate ID、Vikunja task ID、sync状態。
- Vikunja project概要: project名、全件数、未完了、完了。
- Vikunja直近task: ID、タイトル、完了、期限、担当、進捗、更新日時、URL。

LLMにはAPI token、Webhook secret、SQLiteの秘密値を渡さない。外部taskの詳細が必要な場合は、backendが許可した現在状態の要約だけを渡す。

## 会話からタスク候補を作る流れ

```text
ユーザーが相談
  -> ローカルLLMが現在のHub / Tasks概要を参照して回答
  -> 回答とは別に、直近user messageだけを共通v2 promptへ渡す
  -> action / aspirationを根拠付きでvalidatorが判定
  -> 画面に候補カードを表示
  -> ユーザーが「候補として追加」
  -> Hub SQLiteの candidates に pending で保存
  -> 既存の確認待ちキューで編集 / GO / 不要 / アーカイブ
  -> GO時だけVikunja taskを作成
```

P0の既存方針に合わせ、LLMが直接Vikunja taskを作成したり、ユーザー確認なしにGOしたりしない。チャットからの候補も通常入口と同じ確認待ちを通す。

## LLM接続方式

- OpenAI互換 `POST /v1/chat/completions` を使用する。
- 既定接続先はローカル Ollama `http://127.0.0.1:11434/v1`。
- `LOCAL_LLM_BASE_URL` と `LOCAL_LLM_MODEL` で llama.cpp、Ollama、別のOpenAI互換agentへ切り替える。
- 既定providerはOllama。Ollamaでは回答本文を優先するため `think: false` を送る。思考出力を使う場合だけ `LOCAL_LLM_THINK=true` を指定する。
- `LOCAL_LLM_PROVIDER=openai-compatible` を指定した接続にはOllama固有の拡張フィールドを送らない。
- 認証が必要な場合だけ `LOCAL_LLM_API_KEY` を使い、レスポンス・ログ・ブラウザーへ出さない。
- サーバーから到達できない場合は、会話履歴を保持したまま接続エラーを表示する。
- providerが停止・無効・到達不能の場合は、相談の入力欄・送信・サイドウィンドウ起動を閉じ、「ローカルLLMは停止中」と再起動案内を表示する。この状態ではユーザー発言を保存・候補化しない。
- モデルがtool callingに対応する場合は、`get_threadline_context` toolを提示する。非対応モデルではbackendが先に取得したcontextを使うフォールバックにする。
- `get_threadline_context` は読み取り専用で、`all` / `tasks` / `candidates` の範囲を指定できる。タスク登録・GO・編集はLLMへ許可せず、画面上のユーザー操作だけで実行する。

## 候補の検出

相談回答のsystem promptへ候補JSONを混在させない。回答生成後、`apps/web/prompts/threadline-candidate-proposal-v2.txt`を使う独立したLLM呼出へ、直近のuser messageだけを`SOURCE_BODY`として渡す。Hub / Tasks context、assistant回答、過去会話は相談回答には使えても、候補の根拠には使わない。

共通validatorを通過した`action(kind=todo)`と`aspiration(kind=idea)`だけを候補カードとして表示する。aspirationは「やりたい」という原文を保持し、架空の実装作業へ変換しない。壊れたJSON、根拠不一致、候補抽出だけの失敗はカードを出さず、相談回答本文は表示・保存する。

候補カードのボタンは最低限 `候補として追加` とし、追加後は既存確認待ちキューへのリンクを表示する。

## 非機能要件

- 会話履歴はthread単位でSQLiteへ保存する。
- 送信中、接続エラー、空回答、候補追加済みを表示する。
- 画面幅が狭い場合は独立画面を優先し、サイドウィンドウは全幅に近い表示へ縮退する。
- 画面高が短い場合は、独立画面の会話領域を優先し、ページ全体ではなく会話領域内をスクロールさせる。
- XSS防止のため、LLM回答、候補タイトル、タスク名はHTMLエスケープして表示する。
- API token、秘密、raw provider headerを履歴に保存しない。
- 既存の候補・GO・Vikunja連結を変更せず、新しい入口として追加する。
- 1280px幅かつ720px高の画面でも、相談入力と送信操作へ初期表示から到達できる。

## 初版で後回しにするもの

- 複数threadの名前変更・削除。
- ストリーミング表示。
- 画像添付相談。
- LLMが候補を自律的にGOする機能。
- 会話全文のknowledge-vault自動保存。
- 複数モデルを同時比較する機能。

## 関連正本

- データ設計: `docs/data/local-llm-chat-data-design-2026-07.md`
- ランタイムHTTP・provider縮退・回帰: `docs/spec/local-llm-chat-runtime-contract-p0.md`
- 共通AI候補提案: `docs/spec/ai-candidate-proposal-contract-p0.md`
- 実装タスク: `docs/imp/local-llm-chat-intake-tasks.md`
- Hub / Tasks境界: `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
- 現行データ構造ブリーフ: `docs/imp/current-goal-and-data-structure-brief-2026-07-11.md`
