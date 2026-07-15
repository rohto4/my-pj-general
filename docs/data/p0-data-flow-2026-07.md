# P0 データフロー 2026-07

## 目的

P0 の実装済み入口から入った情報が、候補・判断・実行状態へどう変換されるかを固定する。

## 前提

- P0 の入口は `web`、`slack` payload、`knowledge_vault`、`chat`。Misskeyはsource無効のままpayload以降のAI候補化だけを先行実装している。
- Misskeyの外部取得・認証とGoogle Calendarは P0 外。
- 全候補を `pending` で受け、人の GO なしに Vikunja task を作らない。
- Web manualは直接candidateへ入る。Slack / Misskey / knowledge-vault / chatは共通v2でaction / aspirationを検証する。Slack / Misskeyはacceptedをpendingへ直接写像し、chatは提案カードの受理後にpendingへ写像する。knowledge-vault AI batchだけは、許可断片・AI run・提案をlineage tableへ保存してからaccepted提案をcandidate化する。

## データフロー

```mermaid
flowchart LR
    User(["ユーザー<br/>入力・確認・GO"]):::user
    Sources["入力元<br/>Web / Slack payload<br/>knowledge-vault / AI相談"]:::source
    Lineage[("Vault lineage<br/>文書・断片・AI run<br/>検証済み提案")]:::main
    Candidate["Hub候補<br/>本文 / 出典 / 種類<br/>status=pending"]:::main
    Review{"ユーザー判断<br/>編集 / GO<br/>不要 / アーカイブ"}:::decision
    Decision["判断履歴<br/>action / note / time"]:::main
    Task["Vikunja task<br/>実行TODO正本"]:::external
    Link["実行link<br/>candidate / task<br/>sync state"]:::main
    Mirror["実行状態mirror<br/>完了 / 期限 / 担当"]:::main

    User --> Sources
    Sources --> Candidate
    Sources -->|Windows Vault batch| Lineage --> Candidate
    Candidate --> Review
    User --> Review
    Review --> Decision
    Review -->|GO| Task
    Task --> Link
    Task -->|Webhook / 再照合| Mirror
    Link --> Mirror

    classDef user fill:#e8f5e9,stroke:#73b77a,color:#183d1f,stroke-width:2px,font-size:16px,font-weight:bold
    classDef source fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef main fill:#dff3ff,stroke:#5aa4c8,color:#173746,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef decision fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef external fill:#ffe8d6,stroke:#d9965c,color:#4a2a10,stroke-width:1.8px,font-size:16px,font-weight:bold
```

## P0 の正本

| データ | 正本 | 備考 |
| --- | --- | --- |
| source設定 | Hub SQLite `sources` | 有効状態と最終取り込み時刻 |
| Vault取込batch | Hub SQLite `intake_batches` | manifest hash、prompt/model版、取込状態 |
| Vault文書・断片 | Hub SQLite `source_documents` / `source_fragments` | 相対path、content hash、許可excerpt |
| Vault AI処理・提案 | Hub SQLite `ai_runs` / `candidate_proposals` | input/output hash、検証理由、candidate逆引き |
| 候補 | Hub SQLite `candidates` | source / source_path を保持 |
| 候補タグ | Hub SQLite `candidate_tags` | tag master と分離 |
| 判断 | Hub SQLite `decisions` | edited / approved / rejected / archived |
| AI相談 | Hub SQLite `chat_*` | 提案は人の操作後だけ candidate 化 |
| 実行TODO | Vikunja | Hub は編集正本を複製しない |
| 実行link | Hub SQLite `execution_links` | 1候補1taskを基本とする |
| 実行状態 | Hub SQLite `execution_task_state` | Vikunjaの許可済みfieldだけをmirror |
| 同期履歴 | Hub SQLite `source_sync_runs` / `sync_events` / `sync_attempts` | source単位の開始・完了・件数、署名、冪等、失敗・再照合 |

## 不変条件

- AI相談の提案は `chat_task_suggestions` に置き、ユーザー操作後だけ `candidates.status=pending` へ追加する。
- 共通AI提案はactionを`kind=todo`、aspirationを`kind=idea`へ写像する。aspirationの原文を架空の実行作業へ変換しない。
- Vault / Slack / Misskey AI提案は決定的validatorを通過したものだけ`candidates.status=pending`へ写像し、LLMはGOしない。
- Windows絶対root、secretらしい行、provider hidden reasoningをSQLiteへ保存しない。
- 同じ candidate の GO は成功済みlinkを返し、taskを二重作成しない。
- Vikunja task title は実行表示に記録しても、候補 title を勝手に上書きしない。
- token、Webhook secret、provider header は SQLite・画面・会話履歴へ保存しない。
- 本流DBに mock 候補をseedしない。

## P1へ送る設計課題

全入口共通のRaw event store、意味的な重複束ね、PostgreSQL移行は`docs/product/p1-phase-brief-2026-07.md`で導入条件を管理する。knowledge-vault限定lineageはP0実装済みである。
