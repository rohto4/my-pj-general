# P0 入口別 adapter 仕様

> 状態: Web / Slack payload / Windows knowledge-vault AI batchはP0実装済み。AI相談は追加済み。Linuxローカルvault scanは互換経路、Misskey節はP1 PoC候補である。

作成日: 2026-07-09

## 目的

この文書は入口別adapterの責務を定義する。Web / Slack / chatは共通`candidates`へ直接正規化する。Windows knowledge-vaultは、許可断片・AI run・提案をSQLiteへ由来保存してから、検証済み提案だけを`candidates`へ写像する。

詳細な本認証、本 AI、外部 DB サーバはここでは確定しない。2026-07-10 時点の P0 本デモでは、SQLite と最小 API で入口データを確認待ちキューへ流す。

## 実装済みP0の共通契約

すべてのadapterは入口固有payloadをそのまま実行TODOにしない。Web / Slack / chatはP0の直接正規化を維持する。knowledge-vault AI batchだけは、WindowsとLinuxの境界を安全に越え、AI提案の根拠を監査できるよう、`intake_batches` / `source_documents` / `source_fragments` / `ai_runs` / `candidate_proposals`を先行保存する。

```text
source payload
-> adapter
-> candidates (status=pending, source / source_path / excerpt / summary)
-> 確認待ちキュー
-> ユーザーの編集 / GO / 不要 / アーカイブ
-> GO時だけVikunja task
```

`knowledge_vault` と `slack` の取り込みは、候補とは別に `source_sync_runs` へ開始・成功・失敗・件数を残す。batch経路のsource名は`knowledge_vault_batch`とする。Web手入力とAI相談は個別の画面APIを使うが、最終的な候補は同じ`candidates`と確認待ちキューへ入る。

`docs/spec/intake-unified-event-model.md`の汎用Raw入口イベントは引き続きP1候補である。P0で実装したknowledge-vaultの限定lineageは、全入口の汎用event store完成を意味しない。

## 共通の失敗・再実行境界

| 状況 | P0の扱い | 復旧・観測 |
| --- | --- | --- |
| 空本文、対象外行、同一入力済み | 候補を作らず `skipped` と数える | API応答と `/api/observability` の最新sync runで件数を確認する |
| vault / Slack取り込み中の例外 | `source_sync_runs.state=failed` とerrorを記録し、合成候補を作らず呼出元へ失敗を返す | 入力・設定を直して同じpayloadを再実行する。決定的な候補IDにより既存候補は重複作成しない |
| connectorや入力元が未接続 | 他の入口、既存候補、確認待ち、Tasksの実行を止めない | sourceごとの失敗を観測し、当該入口だけを再実行する |

候補の途中作成を含む障害を無条件に削除・再取り込みしない。再実行時は既存IDをskipするため、利用者は実行前後の `scanned` / `created` / `skipped` / `failed` と候補一覧を照合する。

## adapter 別方針

| Adapter | P0 薄く実装 1 版 | P0 完了時点の方向 |
| --- | --- | --- |
| Web manual | drawer から `/api/candidates` へ登録し、SQLite に保存する | 最初の本線入口として維持する |
| Slack | connector / 手動 import payload を `/api/import/slack` へ渡す。対象は `memo-ideas` チャンネルに限定 | Slack API / event / polling のどれで取るかを後続確定する |
| Misskey | P0未接続 | P1 PoCでREST差分取得 / Streaming / experimental Webhookを比較する |
| knowledge-vault | Windows collectorが`records` / `inbox` / `tasks` / `memory`を読み、ローカルLLM提案または限定fallbackをSSH batchでLinux importerへ渡す | content hash、根拠断片、prompt/model版、検証理由を保存し、acceptedだけを`KVAI-*` pending候補へ写像する |

## Web manual adapter

### 入力

- タイトル
- 本文
- URL
- 任意タグ
- 予定化したいかどうかの緩い指定

### P0候補への写像

| Field | 値 |
| --- | --- |
| `source` | `web` |
| `source_path` | 入力URLがある場合だけ保持 |
| `title` / `excerpt` / `summary` | 画面入力から作る候補本文 |
| `occurred` | 入力時刻 |

### 現行HTTP境界

`POST /api/candidates` は妥当な入力を `pending` 候補として保存し、`201` で候補を返す。手入力の作成は判断ログに `created` を残す。画面が応答を受け取れない場合、クライアントは仮の候補を生成せず、失敗理由だけを表示する。

## Slack adapter

### P0 暫定範囲

- 特定チャンネルを対象にする。
- チャンネル名は `memo-ideas`。
- URL は `https://unibell4-dev.slack.com/archives/C0BG4TCPAUD`。
- 全ワークスペース、全チャンネル、全DMは対象外。
- 抽出対象は、やりたいこと、困っていること、タスクっぽいこと。

### P1 source lineageモデル

| Field | 値 |
| --- | --- |
| `source_type` | `slack` |
| `source_ref` | channel id + ts |
| `payload` | message text、thread 情報、reaction 情報の snapshot |
| `source_url` | Slack permalink が取れる場合 |
| `occurred_at` | message ts |

### 初期画面で見せる項目

- チャンネル名
- 投稿者
- 投稿日時
- 本文抜粋
- thread / reaction の有無
- AI 整理結果

### 現行P0のAPI・候補写像

`POST /api/import/slack` は connector または手動payloadの `messages` だけを受ける。各メッセージは `ts + text` のhashから `SL-*` 候補IDを決め、`source=slack`、`source_path=channelUrl`、`status=pending` として保存する。空本文、参加通知、既存IDは `skipped` とし、実行結果の `scanned` / `created` / `skipped` と `syncRun` を返す。

P0は Slack API token、event subscription、全ワークスペース検索をHubのHTTP契約に含めない。connectorが返したpayloadを入力にし、失敗や再実行はsource run単位で扱う。

## Misskey adapter

### P0 暫定範囲

- note payload を Raw として保存できる形を想定する。
- 実接続方式は後続で決める。

### P1 source lineageモデル

| Field | 値 |
| --- | --- |
| `source_type` | `misskey` |
| `source_ref` | note id |
| `payload` | note data snapshot |
| `source_url` | note URL が作れる場合 |
| `occurred_at` | note createdAt |

## knowledge-vault adapter

### P0 暫定範囲

優先対象は次。

```text
G:\knowledge-vault\records\
G:\knowledge-vault\inbox\
G:\knowledge-vault\memory\l1-triggers.md
G:\knowledge-vault\memory\l2-models\
G:\knowledge-vault\tasks\active\
G:\knowledge-vault\tasks\handoff\
```

詳細は `docs/candi-ref/knowledge-vault-current-structure-for-intake.md` を参照する。

対象範囲内は日付やファイル名で細かく絞らず全件をscanする。ただし、候補は未完了の次アクションだけに限定する。

### 抽出対象

- やりたいこと
- 困っていること
- タスクっぽいこと
- 検討したこと
- 知見の種
- 後で判断したいこと
- 後で調べたいこと
- 次アクションや handoff に相当すること

### 現行P0のbatch・候補写像

Windowsの`apps/web/vault_intake.py collect-vault-batch`は、README、完了済みfrontmatter、空文書を除外し、秘密らしい代入行を`[REDACTED_SECRET_LINE]`へ置換してからローカルLLMへ渡す。LLMは版管理promptに従い、文書要約、具体的なtask proposal、完全一致の根拠引用をJSONで返す。

validatorはschema、enum、長さ、可視タグmaster、根拠引用、日付、曖昧titleを決定論的に検査する。LLMなし、timeout、不正JSONでは、`Next Actions`等の明示sectionにある未完了項目だけをfallback提案にする。inbox見出しだけをタスク化しない。

PowerShell wrapperはbatchとmanifestだけを専用SSH鍵で転送する。Linux remote helperがSHA-256を照合し、Hub containerの`db_tool.py import-vault-batch`へstdinで渡す。accepted提案は`KVAI-*`、`source=knowledge_vault`、Vault相対path、根拠excerpt、`status=pending`として保存する。held提案はlineageへ残すが確認待ちには出さない。SQLiteファイルは転送しない。

`POST /api/import/knowledge-vault`の規則ベースLinuxローカルscanは回帰互換のため残すが、管理画面からは起動せず、Windows Vaultの本線には使わない。

### P0 source lineageモデル

| Field | 値 |
| --- | --- |
| `source_type` | `knowledge_vault` |
| `source_ref` | vault relative path + heading / block id 相当 |
| `payload` | 相対path、mtime、許可excerpt、文書要約、AI構造化提案 |
| `source_url` | ローカル path または Obsidian link 相当 |
| `occurred_at` | file mtime または文中日付 |
| `content_hash` | excerpt または block の hash |

## P0 本デモ状態の扱い

- Web manual は画面から実入力し、SQLite に永続化する。
- Slack は `memo-ideas` connector の読み取りを確認済み。現時点で対象投稿はないため、P0では import payload 経路を用意する。
- Misskey sourceは無効設定として保持し、P1 PoCまで実データ・mock候補のどちらも本流へ入れない。
- knowledge-vaultはWindows AI batchを本線とし、許可断片とAI処理履歴をLinux SQLiteへ保存する。本文全体・見出し・完了記録をそのままTODO化しない。
- すべての AI 整理結果は確認待ちキューに入り、自動 GO はしない。

## 回帰・受入根拠

| 確認対象 | 自動根拠 | 実機で確認すること |
| --- | --- | --- |
| vault scanの共通domain | `apps/web/test/test_source_sync.py` | 有効scopeの取込結果と対象外scopeが混ざらないこと |
| Windows AI batchのprompt・根拠検証・縮退・lineage・冪等性 | `apps/web/test/test_vault_intake.py` | ローカルLLMの正解セット評価後、pending候補の原文忠実度を確認すること |
| SSH batchのhash・単独SQLite writer | `infra/intake/test_import_knowledge_vault.py` | dry-run後に専用鍵で1batchを送り、`knowledge_vault_batch` runを確認すること |
| Slackの成功・重複skip・観測 | `apps/web/test/api.test.mjs` の source同期・observabilityテスト | connector payloadを使った件数と、再実行時の`skipped`を確認すること |
| 手入力の永続化・失敗時非合成 | `apps/web/test/api.test.mjs` の候補作成/SQLite応答テスト | 実データを変更する入力はユーザー確認後だけに行うこと |

実装を読む必要があるのは、adapterの候補写像・同期run・再実行規則を変更するときだけである。legacy scanは`apps/web/source_sync.py`、Windows batchは`apps/web/vault_intake.py`、SQLite境界は`apps/web/db_tool.py`と対応testだけを読む。

## P0 では決めないこと

- アプリ本体へ Slack API 認証を持たせる方式。
- Misskey の受信方式。
- source_refを跨ぐ意味的な類似束ね。
- 自動 dedupe の厳密条件。
- 部分自動確定の条件。

## 関連文書

- `docs/spec/intake-unified-event-model.md`
- `docs/spec/knowledge-vault-ai-intake-contract-p0.md`
- `docs/data/knowledge-vault-ai-intake-data-design-2026-07.md`
- `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`
- `docs/ops/knowledge-vault-ai-intake-runbook-2026-07.md`
- `docs/data/p0-data-flow-2026-07.md`
- `docs/spec/confirmation-queue-p0.md`
- `docs/spec/ai-assisted-registration-flow.md`
- `docs/ops/p0-operations-runbook-2026-07.md`
- `docs/candi-ref/knowledge-vault-current-structure-for-intake.md`
- `docs/candi-ref/ui-reference-sources-for-initial-prototype.md`
