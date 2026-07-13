# P0 ローカルLLM相談ランタイム契約

## 目的と範囲

この文書は、実装済みP0のローカルLLM相談について、HTTP境界、保存状態、読み取り境界、障害時の振る舞い、回帰根拠を定義する。画面体験は `docs/product/local-llm-chat-intake-2026-07.md`、SQLiteのtable/fieldは `docs/data/local-llm-chat-data-design-2026-07.md` を正本とする。

LLMは回答と候補提案を行う補助である。候補を直接作成・編集・GOしたり、Vikunja taskを直接作成したりしない。

## HTTP契約

| HTTP境界 | 成功 | 失敗・非動作 | 永続化境界 |
| --- | --- | --- | --- |
| `GET /api/chat/bootstrap` | thread、直近message、提案、公開可能な接続状態、許可済みcontext要約を返す | 依存が未設定または到達不能でも、Hubの候補・Tasksを変えない | 必要なら既定threadを作る。API key、secret、raw headerは返さない |
| `POST /api/chat/messages` | ユーザー発言、LLM回答、解析済み提案を返す | 空入力は`400`。provider失敗は`502`と保存済みユーザー発言を返し、候補・GOを起こさない | ユーザー発言はLLM呼出前に保存する。成功した回答と提案だけを保存する |
| `POST /api/chat/suggestions/:id/accept` | 提案を既存`candidates`へ`pending`、`source=chat`で作り`201`を返す | 存在しない提案は失敗とし、別候補を合成しない | 受理済み提案は同じcandidateを返す。以後は通常の確認待ちキューだけが編集・GOを担う |

提案ブロックは画面表示用の回答本文から除去し、構造化候補としてだけ保存する。候補のtitle、summary、todo、kind、schedule、confidence、missingは通常のcandidate形式へ写像する。

## provider と tool の境界

| 境界 | 契約 |
| --- | --- |
| provider | 既定はOllama互換のOpenAI互換HTTP API。`LOCAL_LLM_PROVIDER=openai-compatible` ではOllama固有fieldを送らない |
| 設定 | base URL、model、timeout、tool有効化、Ollamaの`think`をserver環境変数で設定する。API keyはserverだけが保持する |
| context tool | `get_threadline_context` は`all` / `tasks` / `candidates`の許可済み要約だけを返す。書き込みtoolは提供しない |
| 秘密 | API token、Webhook secret、SQLiteの秘密、raw provider headerをprompt、message、metadata、公開設定へ入れない |

## 縮退と復旧

- OllamaまたはOpenAI互換endpointが停止・未設定でも、Hub、確認待ち、Vikunja導線、既存会話履歴は維持する。相談送信だけが一般化した接続エラーになる。
- `/api/health` は依存が設定済みで到達不能なら`degraded`、明示無効なら正常な非有効状態として返す。接続URLや認証情報は返さない。
- 運用者はproviderを復旧または設定を修正してhealthを再確認する。失敗した送信は自動で候補化されないため、利用者は保存済みの発言を確認して必要なら再送する。
- provider障害を理由に候補、判断、execution link、Vikunja taskをrollbackまたは再作成しない。

## 回帰・受入根拠

| 確認対象 | 根拠 |
| --- | --- |
| 会話保存、`think:false`、提案受理後のpending候補化、秘密の非公開 | `apps/web/test/api.test.mjs` の「ローカルLLM相談は会話を保存し、候補を確認待ちへ追加できる」 |
| scope付きread-only toolと回答継続 | 同testの「ローカルLLMエージェントのcontext toolは指定scopeだけを読み取り、回答生成を継続する」 |
| 到達不能依存の短時間`degraded`と秘密非露出 | 同testの「healthは設定済み依存へ到達できない時も短時間でdegradedを返す」 |
| 実画面の会話・候補追加・停止時縮退 | `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` の対象ID。実機受入は自動回帰と別管理 |

実装を読む必要があるのはprovider形式、tool範囲、message保存、HTTP statusを変更するときだけである。その場合は `apps/web/server.mjs`、`apps/web/db_tool.py`、上記testだけを読む。

## 非対象

- LLMによる自律的な候補登録、GO、Vikunja編集。
- provider側への会話履歴永続化。
- 外部公開LLM endpointの認証・firewall設計。
- 部分自動確定のしきい値。

## 関連正本

- `docs/product/local-llm-chat-intake-2026-07.md`
- `docs/data/local-llm-chat-data-design-2026-07.md`
- `docs/spec/confirmation-queue-p0.md`
- `docs/spec/hub-ui-interaction-contract-p0.md`
- `docs/ops/p0-operations-runbook-2026-07.md`
