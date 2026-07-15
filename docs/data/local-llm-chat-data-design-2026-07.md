# ローカルLLM相談窓口 データ設計 2026-07

作成日: 2026-07-11

## 所有権

チャットthreadと会話履歴はHub SQLiteの正本とする。LLM provider側へ履歴を永続保存する前提にはしない。候補として受理したデータは既存 `candidates` と `decisions` を正本とする。共通提案の`action / aspiration`は、重複fieldを増やさず`chat_task_suggestions.kind`と`candidates.kind`の`todo / idea`で保持する。

## 追加テーブル

```sql
create table if not exists chat_threads (
  id text primary key,
  title text not null,
  provider text not null,
  model text not null,
  status text not null default 'active',
  created_at text not null,
  updated_at text not null
);

create table if not exists chat_messages (
  id integer primary key autoincrement,
  thread_id text not null,
  role text not null,
  content text not null,
  metadata_json text not null default '{}',
  created_at text not null
);

create table if not exists chat_task_suggestions (
  id text primary key,
  thread_id text not null,
  message_id integer not null,
  title text not null,
  summary text not null,
  todo text not null,
  kind text not null,
  schedule text not null,
  confidence text not null,
  missing_json text not null default '[]',
  status text not null default 'proposed',
  candidate_id text,
  created_at text not null,
  updated_at text not null
);
```

## 状態

```text
thread: active -> archived
suggestion: proposed -> accepted -> candidate_pending
suggestion: proposed -> dismissed
```

`candidate_pending` は既存 `candidates.status=pending` と対応する。ユーザーが確認待ちキューでGOした後は、既存の `execution_links` と `execution_task_state` を使う。chat側にVikunja taskの複製テーブルは追加しない。

## API

| API | 用途 |
| --- | --- |
| `GET /api/chat/bootstrap` | 現在thread、履歴、候補、LLM接続状態、現在contextの要約を返す |
| `POST /api/chat/messages` | ユーザー発言を保存して相談回答を生成し、別呼出で直近user messageだけを共通v2へ渡して候補提案を返す。agentが要求した読み取り専用context toolは相談回答側だけでbackendが仲介する |
| `POST /api/chat/suggestions/:id/accept` | 候補提案を既存 `candidates` へpendingで作成する |

## provider境界

`apps/web/server.mjs` は OpenAI互換APIへ接続する。provider-specificなAPI形式をHub内部へ持ち込まない。

```text
LOCAL_LLM_BASE_URL  default: http://127.0.0.1:11434/v1
LOCAL_LLM_MODEL     default: gemma4:latest
LOCAL_LLM_API_KEY   optional, server env only
LOCAL_LLM_TIMEOUT_MS default: 60000
LOCAL_LLM_PROVIDER  default: ollama when no custom base URL is set
LOCAL_LLM_THINK     default: false for Ollama
```

Ollamaの思考モデルは、既定設定では内部思考側へ出力が寄り、回答本文が空になる場合がある。そのため相談窓口では既定で `think: false` を指定する。汎用OpenAI互換providerへはこのOllama固有フィールドを送らない。

Linux上のHubからWindowsのLLMを使う場合は、`127.0.0.1`ではなくLAN到達可能なOpenAI互換agent URLを設定する。LLM endpointを外部公開する場合の認証・ファイアウォールはインフラ作業として別管理する。

## データ保持と安全性

- 相談回答LLMへ送るcontextは候補・実行状態の要約だけに制限する。候補抽出LLMへは直近user message、source ref、許可タグだけを送り、contextとassistant回答を送らない。
- `get_threadline_context` は `all` / `tasks` / `candidates` のscopeを受け、backendが許可した要約だけを返す。書き込みtoolはP0では提供しない。
- API tokenやWebhook secretをsystem prompt、chat message、metadataへ入れない。
- 相談回答LLMの本文は表示用assistant messageとして保存する。候補抽出LLMのraw JSONはchat履歴へ保存せず、validator通過fieldだけを`chat_task_suggestions`へ保存する。
- provider errorは履歴へ秘密を含めず、UIへ一般化した接続エラーとして返す。

HTTP status、provider障害時の保存順、toolの読取範囲、回帰根拠は `docs/spec/local-llm-chat-runtime-contract-p0.md` を正本とする。
候補分類、根拠、非具体化、source別入力は `docs/spec/ai-candidate-proposal-contract-p0.md` を正本とする。
