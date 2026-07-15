# Windows knowledge-vault AI取込アーキテクチャ 2026-07

## 目的

Windowsの`G:\knowledge-vault`を読み、ローカルLLMによる要約・タスク提案を、Linux上のHub SQLiteへ由来付きで安全に格納する。LLMは提案だけを作り、Hub候補の確認、GO、Vikunja task作成の既存境界を越えない。

## 採用構成

```mermaid
flowchart LR
    Vault["Windows Vault<br/>許可scopeのMarkdown"]:::input
    Collector["Windows Collector<br/>差分・断片・hash"]:::api
    LLM["ローカルLLM<br/>要約・提案JSON"]:::async
    Validator{"決定的validator<br/>schema・根拠・重複"}:::decision
    Batch["SSH batch<br/>manifest・SHA-256"]:::external
    Store[("Linux Hub SQLite<br/>原文断片・AI run・提案")]:::data
    Queue["Hub確認待ち<br/>pending候補"]:::app
    Tasks["Vikunja Tasks<br/>GO後の実行正本"]:::external

    Vault --> Collector --> LLM --> Validator --> Batch --> Store --> Queue --> Tasks
    Collector -.->|LLM停止時は明示actionだけ| Validator

    classDef input fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.5px
    classDef app fill:#fff4c2,stroke:#d8b545,color:#3b3100,stroke-width:1.5px
    classDef api fill:#e8f5e9,stroke:#73b77a,color:#183d1f,stroke-width:1.5px
    classDef async fill:#f3e8ff,stroke:#a986d8,color:#302044,stroke-width:1.5px
    classDef data fill:#dff3ff,stroke:#5aa4c8,color:#173746,stroke-width:1.5px
    classDef external fill:#ffe8d6,stroke:#d9965c,color:#4a2a10,stroke-width:1.5px
    classDef decision fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.5px
```

## 責務シーケンス

### Windows収集・AI提案・Linux取込

```mermaid
sequenceDiagram
    autonumber
    box rgb(227, 242, 253) Windows source
        participant V as knowledge-vault
    end
    box rgb(232, 245, 233) Windows intake
        participant W as Collector / Validator
        participant L as ローカルLLM
    end
    box rgb(255, 232, 214) Linux boundary
        participant H as Hub Importer / SQLite
    end

    W->>V: allowlist内MarkdownをUTF-8で差分scan
    V-->>W: 相対path・許可本文
    W->>W: 秘密らしい行を伏せ、断片化・content hash
    W->>L: 共通v2 prompt・許可タグ・source ref
    alt LLM応答が正常
        L-->>W: 要約・action / aspiration・完全一致根拠JSON
        W->>W: schema・引用・enum・完了・重複を決定的検証
    else 未設定・timeout・不正JSON
        L--xW: 一般化した失敗
        W->>W: 明示された未完了actionだけをfallback提案
    end
    W->>W: batch・manifest・SHA-256を生成
    W->>H: 専用SSH鍵でbatchとmanifestだけを転送
    H->>H: hash・schema・versionを検証
    alt batchが有効
        H->>H: transactionでlineageを冪等保存
        H->>H: acceptedだけをpending候補へ写像
        H-->>W: scanned / accepted / held / skipped
    else 不一致・未知version
        H--xW: SQLite無変更でbatchを拒否
    end

    Note over W,H: SQLite本体・secret・Vault全文は転送しない
```

### Hub確認・GO後の実行

```mermaid
sequenceDiagram
    autonumber
    box rgb(255, 244, 194) Review
        actor U as 利用者
        participant H as Hub確認待ち
    end
    box rgb(255, 232, 214) Execution
        participant T as Vikunja Tasks
    end

    H-->>U: pending候補と原文根拠を表示
    U->>H: 編集 / 不要 / アーカイブ
    alt 利用者がGO
        U->>H: GOを確定
        H->>T: 実行TODOを一方向登録
        T-->>H: task ID・実行状態
        H-->>U: 登録結果とmirror状態を表示
    else GOしない
        H-->>U: Hub内の判断状態だけを保持
    end

    Note over H,T: LLM・ImporterはGOもVikunja更新も行わない
```

### 図中の禁止境界

- Windows collectorはSQLiteへ書かず、秘密をbatchへ残さない。
- ローカルLLMはcandidate / Tasksを直接更新せず、aspirationへ架空の期限・担当・Project・具体作業を補完しない。
- validatorはLLMの自己申告confidenceだけで採否を決めない。
- SSH transportはSQLiteファイルを転送せず、新しいLAN書込APIを公開しない。
- Linux importerはVaultへ逆書きせず、自動GOやVikunja直接更新をしない。
- LLM障害を理由に、既存候補や既存taskをrollbackしない。

## 障害境界

- LLM未設定・timeout・不正JSONでは、明示された未完了`Next Actions`だけを規則ベース提案にする。推測候補は作らない。
- 1文書のLLM失敗はbatch全体を破棄せず、`ai_runs.status=fallback`として残す。
- manifest不一致、schema不一致、未知のversionはLinux SQLiteを書かずに失敗する。
- 同じ`batch_id`、`document_id`、`proposal_id`の再取込は既存行を返し、candidateを二重作成しない。
- LinuxだけをSQLite writerとし、Windows共有ドライブやSCPでSQLite本体を扱わない。

## 実装境界

- collector / validator / importer: `apps/web/vault_intake.py`
- 共通候補契約: `docs/spec/ai-candidate-proposal-contract-p0.md`
- prompt正本: `apps/web/prompts/threadline-candidate-proposal-v2.txt`
- 決定的validator: `apps/web/candidate_proposal.py`
- SQLite: `apps/web/db_tool.py`
- Windows→Linux運用: `infra/intake/import-knowledge-vault.ps1`、`infra/intake/import-knowledge-vault-remote.sh`
- 回帰: `apps/web/test/test_vault_intake.py`、`infra/intake/test_import_knowledge_vault.py`

## 関連正本

- `docs/spec/knowledge-vault-ai-intake-contract-p0.md`
- `docs/data/knowledge-vault-ai-intake-data-design-2026-07.md`
- `docs/ops/knowledge-vault-ai-intake-runbook-2026-07.md`
- `docs/spec/intake-source-adapters.md`
- `docs/spec/confirmation-queue-p0.md`
