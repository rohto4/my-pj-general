# knowledge-vault AI取込契約 P0

## 範囲

Windows上のknowledge-vaultを文書単位で収集し、任意のローカルLLMで要約・候補提案を作り、検証済みbatchをLinux Hubへ取り込む。候補判定の共通契約は`docs/spec/ai-candidate-proposal-contract-p0.md`を正本とする。現行`POST /api/import/knowledge-vault`のLinuxローカルscanは互換経路として残すが、Windows Vaultの本線はbatch経路とする。

## 利用者フロー

1. 利用者またはWindows Task Schedulerがcollectorを起動する。
2. collectorは許可scopeの更新が新しいMarkdownを読み、文書要約と0件以上の提案をbatchへ書く。
3. 専用SSH鍵でbatchをLinuxへ送り、hash照合後にHub container内のimporterへ渡す。
4. 検証済み提案はHubの`pending`候補として表示される。保留提案はlineageだけを保存し、確認待ちには出さない。
5. 利用者がHubで編集・不要・アーカイブ・GOを判断する。GO後だけVikunja taskを作る。

## collector契約

| 項目 | 契約 |
| --- | --- |
| 対象 | `records`、`inbox`、`tasks`、`memory`のうち管理画面で有効なscope。README、完了/archived frontmatter、空文書は除外 |
| 上限 | 既定30文書。更新日時降順。1文書のLLM入力は12,000文字まで |
| 文字 | UTF-8 / UTF-8 BOMを受理し、batchはUTF-8 JSONで出力 |
| ID | 相対pathとcontent hashからdocument ID、文書IDと提案内容からproposal IDを決定的に作る |
| LLM | OpenAI互換`/chat/completions`。temperature 0、stream無効。API keyは環境変数のみ |
| 縮退 | LLMなし/失敗時は明示action節の未完了項目だけを提案。inbox見出しだけでは候補にしない |

## prompt・出力契約

runtime promptは`apps/web/prompts/threadline-candidate-proposal-v3.txt`を実行正本とし、`prompt_version=threadline-candidate-proposal-v3`をbatchとAI runへ保存する。v2と旧`knowledge-vault-task-proposal-v1.txt`は過去実行の意味を復元する履歴として残す。Ollama互換endpointでは完全な候補JSONを途中で切らないため、clientの出力上限を3,000 tokenにする。

出力はJSON objectだけとし、文書全体の`document_summary`と`candidate_proposals`を返す。各提案は`proposal_type=action|aspiration`を持ち、actionは`kind=todo`、aspirationは`kind=idea`へ写像する。各提案は次を満たす。

- actionの`title`と`todo`は対象・行動・期待結果が分かる。単独の「確認する」「整理する」「対応する」は不可。
- aspirationは本人の希望表現を根拠にし、`todo`を完全一致引用と同じにする。原文にない実装方法、期限、次作業へ具体化しない。
- `summary`は原文の事実・目的・制約だけを1〜2文で書く。
- `evidence_quotes`は入力本文からの完全一致引用を1件以上持つ。
- 固有名詞、コマンド、path、識別子は勝手に翻訳・一般化しない。
- 完了、却下、履歴、例示、テンプレート、他者の引用を新規タスクにしない。
- owner、期限、Project、優先度は原文に明記されない限り補完しない。
- `schedule`は原文に明示された有効な`YYYY-MM-DD`だけ。それ以外は`候補なし`。
- `tags`は入力で渡した可視タグmasterの値だけを使う。
- 不確実なら提案しないか、`missing`に不足を記録する。

## validator契約

acceptedにするには、必須field、enum、長さ、許可タグ、完全一致引用、日付形式、種類ごとのkind、actionの具体的title、aspirationの原文保持を全て満たす必要がある。同じ根拠のaction / aspirationはactionだけを残す。失敗理由は`validation_json`へ保存する。LLMの`confidence`は表示補助であり、accepted判定を上書きしない。

## import契約

`db_tool.py import-vault-batch`はbatch JSONをstdinで受ける。未知version、不正ID、根拠不一致ではtransactionをcommitしない。同じbatchの再送は`duplicate=true`で成功し、既存candidateを返す。

accepted提案のcandidate写像:

| Candidate field | 値 |
| --- | --- |
| `id` | `KVAI-` + proposal hash |
| `status` | `pending` |
| `source_id` | `knowledge_vault` |
| `source_path` | Vault相対path。Windows絶対pathは保存しない |
| `title` / `summary` / `todo` | 検証済みproposal |
| `excerpt` | evidence quote |
| `confidence` | proposal値。ただし自動GO条件には使わない |
| `tags` | `knowledge-vault`、scope、`ai-proposed`と許可タグ |

候補種別は`proposal_type`をbatch JSONに保持し、Hub candidateでは`kind=todo|idea`として保持する。既存SQLite tableへ重複fieldは追加しない。

## 非動作

- 自動GO、自動Vikunja登録、自動期限確定。
- WindowsからLinux SQLiteへの直接接続・ファイル共有。
- providerのhidden reasoning保存。
- secret、token、環境変数全文、Vault絶対rootのSQLite保存。
