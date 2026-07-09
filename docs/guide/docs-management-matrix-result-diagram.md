# docs 管理マトリクス結果図

## 目的

この文書は、`docs/guide/docs-management-rules.md` のマトリクス結果を図で把握するための要約である。

結論は、`正本を1つ決める`、`同期先には要約・リンク・状態だけ置く`、`進行管理とセッション記録を正本化しない` の3点である。

## 正本と同期先の全体像

```mermaid
flowchart LR
    Root["実行・入口ルール<br/>AGENTS / PROJECT<br/>README"]:::input
    Guide["docs 管理ルール<br/>docs/guide<br/>正本関係マトリクス"]:::other
    Product["体験・要件<br/>docs/product<br/>ユーザー価値"]:::output
    Spec["確定仕様<br/>docs/spec<br/>状態・操作・連携"]:::output
    Data["データ正本<br/>docs/data<br/>object / event"]:::output
    Arch["構成・採用判断<br/>docs/arch<br/>tech-stack"]:::output
    Imp["進行管理<br/>docs/imp<br/>判断待ち・TODO・完了"]:::output
    Diary["セッション記録<br/>docs/diary<br/>handoff"]:::output
    Candi["候補・比較<br/>docs/candi-ref<br/>未採用案"]:::output
    Vault["横断知識<br/>knowledge-vault<br/>再利用原則"]:::output

    Root -->|参照| Guide
    Guide -->|配置ルール| Product
    Guide -->|配置ルール| Spec
    Guide -->|配置ルール| Data
    Guide -->|配置ルール| Arch
    Product -->|確定した振る舞い| Spec
    Spec -->|必要な項目| Data
    Arch -->|採用済み技術| Root
    Candi -->|採用・不採用判断| Arch
    Product -->|未決・次アクション| Imp
    Spec -->|未決・実装待ち| Imp
    Data -->|未決・整備待ち| Imp
    Diary -->|最新状態を戻す| Imp
    Imp -->|引き継ぎ要約| Diary
    Guide -->|横断化できる原則| Vault

    classDef input fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.7px,font-size:15px,font-weight:bold
    classDef output fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.7px,font-size:14px,font-weight:bold
    classDef other fill:#f5f7fa,stroke:#aab4c0,color:#26313f,stroke-width:1.4px,font-size:14px,font-weight:normal
```

## 更新漏れしないための仕組み

```mermaid
flowchart LR
    Event["運用イベント<br/>タスク・判断・仕様<br/>比較・handoff"]:::input
    Policy["更新ポリシー<br/>docs-management-rules<br/>タイミング別判断表"]:::other
    Owner{"正本を<br/>決める"}:::other
    Canon["正本更新<br/>product / spec / data<br/>arch / guide"]:::output
    Progress["進行管理更新<br/>docs/imp<br/>判断待ち・TODO・完了"]:::output
    Entry["入口同期<br/>AGENTS / PROJECT<br/>README / docs README"]:::output
    Diary["handoff<br/>docs/diary<br/>必要時だけ"]:::output
    VaultGate{"記録対象<br/>あり?"}:::other
    Vault["knowledge-vault<br/>中央policy<br/>既存カテゴリ"]:::output
    Check["終了前チェック<br/>imp・正本・入口<br/>vault反映確認"]:::other

    Event --> Policy --> Owner
    Owner --> Canon
    Owner --> Progress
    Owner --> Entry
    Owner --> Diary
    Owner --> VaultGate
    VaultGate -->|あり| Vault
    VaultGate -->|なし| Check
    Canon --> Check
    Progress --> Check
    Entry --> Check
    Diary --> Check
    Vault --> Check

    classDef input fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.7px,font-size:15px,font-weight:bold
    classDef output fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.7px,font-size:14px,font-weight:bold
    classDef other fill:#f5f7fa,stroke:#aab4c0,color:#26313f,stroke-width:1.4px,font-size:14px,font-weight:normal
```

## タイミング別更新ゲート

```mermaid
flowchart LR
    Event["運用イベント<br/>タスク整理・進捗<br/>判断待ち・完了"]:::input
    Policy["docs update policy<br/>docs-management-rules<br/>タイミング別判断表"]:::other
    Imp["進行管理更新<br/>docs/imp<br/>TODO・判断・完了"]:::output
    Source["正本更新<br/>product / spec / data<br/>arch / guide"]:::output
    Diary["handoff<br/>docs/diary<br/>必要時だけ"]:::output
    VaultGate{"記録価値<br/>あり?"}:::other
    Vault["knowledge-vault<br/>中央policyに従う"]:::output

    Event --> Policy
    Policy --> Imp
    Policy --> Source
    Policy --> Diary
    Policy --> VaultGate
    VaultGate -->|あり| Vault
    VaultGate -->|なし| Imp

    classDef input fill:#e3f2fd,stroke:#64a6d9,color:#17324d,stroke-width:1.7px,font-size:15px,font-weight:bold
    classDef output fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.7px,font-size:14px,font-weight:bold
    classDef other fill:#f5f7fa,stroke:#aab4c0,color:#26313f,stroke-width:1.4px,font-size:14px,font-weight:normal
```

## 読み取り

- 色分けは、入力口を青、出力先を赤、その他の判断・ルール・確認をグレーに統一する。
- `docs/guide/docs-management-rules.md` が docs 配置と相互更新ルールの正本である。
- タスク整理、進捗、判断待ち、完了、handoff の各タイミングでは、`docs/guide/docs-management-rules.md` のタイミング別更新判断表を見る。
- 変更が起きたら、まず正本を決め、正本、進行管理、入口、handoff、knowledge-vault の順に更新要否を判定する。
- `docs/imp/*` は判断待ち、実装待ち、完了記録を追うための正本であり、作業状態はここから復元できるようにする。
- `AGENTS.md`、`PROJECT.md`、`README.md`、`docs/README.md` は入口同期先であり、重要文書の追加や起動ルール変更時にだけ必要最小限で更新する。
- knowledge-vault へは、横断的な知見だけでなく、判断経緯や後から復元価値のある作業記録も中央 policy に従って反映する。
- `docs/diary/*` は最新状況を知る入口にはなるが、最新状態の正本にはしない。
- `docs/spec/*`、`docs/product/*`、`docs/data/*`、`docs/arch/*` には確定した設計内容を置き、TODO や判断待ちを長く残さない。
- `docs/candi-ref/*` の比較が採用・不採用判断に変わったら、`docs/arch/*` または `tech-stack.md` へ昇格させる。
- 最終報告や handoff 前に、`docs-management-rules.md` のセッション終了時チェックで更新漏れを確認する。
