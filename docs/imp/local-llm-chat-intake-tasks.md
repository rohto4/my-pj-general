# ローカルLLM相談窓口 実装タスク

作成日: 2026-07-11

## 実装

- [x] Ollama / llama.cpp のOpenAI互換endpointを確認する
- [x] 独立画面とサイドウィンドウのUX境界を定義する
- [x] chat thread / message / suggestionのSQLite設計を定義する
- [x] chat用SQLite schemaとbootstrapを追加する
- [x] OpenAI互換LLM adapterとtimeout/error handlingを追加する
- [x] Hub候補・Vikunja概要をcontextとしてLLMへ渡す
- [x] agentの読み取り専用context toolと `all` / `tasks` / `candidates` scopeを追加する
- [x] task proposal構造化ブロックをparseする
- [x] 候補提案を既存candidatesへpendingで追加する
- [x] 独立相談画面 `/chat` を追加する
- [x] dashboard等から開けるサイドウィンドウを追加する
- [x] 会話履歴と候補追加のunit / integration testを追加する
- [x] Ollama実endpointで送受信を確認する
- [x] P0既存導線、GO、Vikunja概要、SQLiteの回帰を確認する
- [x] 会話を主役にした独立画面へ再構成し、接続状態と確認待ちへの導線を1行へ集約する
- [x] provider / model、参照context、候補化前の確認境界を画面に表示する
- [x] 短文メッセージの縦潰れ、暗色statusの低コントラスト、画面外composerを修正する
- [x] 空会話に役割説明と入力用スターターを表示する
- [x] 左サイドメニューへ常設のサイド相談ボタンを追加する
- [x] 説明用の大見出しと3段階フローを除去し、contextを圧縮して残り高を会話領域へ割り当てる
- [x] 入力欄と送信ボタンを同じ行へ配置し、高さ900px / 650pxの段階的な文字・余白縮小を追加する

## 実装済みの接続設定

- 既定: Ollama `http://127.0.0.1:11434/v1` / `gemma4:latest`
- 切替: `LOCAL_LLM_BASE_URL`、`LOCAL_LLM_MODEL`、`LOCAL_LLM_PROVIDER`
- 任意: `LOCAL_LLM_API_KEY`、`LOCAL_LLM_TIMEOUT_MS`、`LOCAL_LLM_ENABLE_TOOLS`
- Ollamaの思考出力は初期値で無効。必要な場合だけ `LOCAL_LLM_THINK=true` を指定する。

## 検証結果 2026-07-11

- 固定応答のAPI統合テストで、会話保存、構造化候補、`pending`候補追加、再読込を確認した。
- Ollama `gemma4:latest` の実endpointで回答本文 `OK.` を受信した。
- context tool呼び出し経路で、Tasks scopeだけを返して回答を継続する統合テストを追加した。
- `apps/web/check.ps1`、Node 12件、Python 3件が成功した。

## UI再設計・実接続検証 2026-07-12

- 1280 x 720の実画面を監査し、会話の縦潰れ、status文字の低コントラスト、入力欄が初期表示外へ落ちる問題を確認して修正した。
- 独立画面を、横一列context、全幅会話、常時到達できるcomposerへ再構成した。初回の3段階説明は後続調整で除去した。
- Hub公開設定は `ollama / gemma4:latest`、接続先はWindows版Ollama `127.0.0.1:11434`、モデルは8.0B / Q4_K_Mと確認した。
- 実推論で `OK` を受信し、Ollama `/api/ps` でロード量 `3281644419 bytes` と `size_vram=3281644419` の一致を確認した。
- UI契約テストを追加し、`apps/web/check.ps1` を通過した。
- 追加調整で、1280 x 720時にdocument overflowなし、live context 26px、message領域533px、入力・送信各52pxを確保した。
- CSSの `max-height: 900px` と `max-height: 650px` でAI相談内だけを段階的に縮小し、4K縦3分割相当の短いviewportへ対応した。
- 左メニューの常設操作から、620px幅・画面高720pxのサイド相談が開くことを実操作で確認した。
- Node回帰18件、`apps/web/check.ps1`、`git diff --check`が成功した。

## 初版受入条件

- OllamaまたはOpenAI互換ローカルLLMへ相談を送信できる。
- 会話履歴をリロード後も表示できる。
- 現在のHub候補とTasks概要を踏まえた回答を得られる。
- LLMがタスクらしさを検出した場合、画面に候補カードと確認ボタンが出る。
- ボタンで既存確認待ちキューへ `pending` 候補を追加できる。
- 追加候補は既存の編集 / GO / 不要 / アーカイブ操作を使える。
- `/chat` 独立画面とサイドウィンドウが同じthreadを表示する。
- LLM停止時も既存Hub画面と会話履歴が壊れない。
