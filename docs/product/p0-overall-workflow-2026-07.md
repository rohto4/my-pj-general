# P0 全体要約ワークフロー図 2026-07

## 目的

この文書は、P0 でユーザーがどんな流れを使えるようになるかを、業務目線で要約したワークフロー図である。

技術構成ではなく、`思いつきが入ってから整理され、TODO 化され、必要なら予定化されるまで` の全体像を固定する。

## P0 の達成条件

- `web 手入力`
- `Slack`
- `Misskey`
- `knowledge-vault`

この 4 入口から情報を受けられること。

そのうえで、次がつながること。

- プール
- AI 整理
- ユーザー GO
- TODO 化
- 必要なら予定化
- ガント表示

## 全体要約ワークフロー

```mermaid
flowchart LR
    User(["ユーザー<br/>確認・GO<br/>訂正入力"]):::user
    Sources["4入口<br/>Web / Slack / Misskey<br/>knowledge-vault"]:::inputMain
    Pool["プール<br/>思いつき・話題・候補"]:::main
    AI["自動処理<br/>AI整理<br/>タグ・要約・候補化"]:::auto
    Review{"ユーザー操作<br/>整理後候補一覧<br/>GO / 保留 / 修正"}:::decision
    Register["昇格 / 登録<br/>アイデア・検討事項<br/>気になる事・TODO"]:::main
    Schedule["予定化<br/>候補は自動生成<br/>登録はユーザーGO"]:::main
    Dashboard["見える化<br/>横断ダッシュボード<br/>現在地を確認"]:::main

    TodoNote["TODO補足<br/>タイトル / 所要時間案<br/>関連リンク / タグ"]:::support
    CodexNote["Codex支援<br/>フォルダ作成<br/>初期プロンプト出力"]:::support

    User -->|手入力| Sources
    User -->|確認・修正| Review
    User -->|登録GO| Register
    User -->|Calendar GO| Schedule
    Sources --> Pool
    Pool --> AI
    AI --> Review
    Review -->|まだ| Pool
    Review -->|GO| Register
    Register --> Schedule
    Schedule --> Dashboard
    Register -.-> TodoNote
    Dashboard -.-> CodexNote

    classDef user fill:#e8f5e9,stroke:#73b77a,color:#183d1f,stroke-width:2px,font-size:16px,font-weight:bold
    classDef inputMain fill:#fff0e4,stroke:#d9965c,color:#4a2a10,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef main fill:#ffe8d6,stroke:#d9965c,color:#4a2a10,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef auto fill:#f3e8ff,stroke:#a986d8,color:#302044,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef decision fill:#fff0f0,stroke:#d87878,color:#4a1515,stroke-width:1.8px,font-size:16px,font-weight:bold
    classDef support fill:#f5f7fa,stroke:#aab4c0,color:#26313f,stroke-width:1.2px,font-size:13px,font-weight:normal
```

## この図で固定したいこと

- 入口は 4 つでも、まずは `入口イベント` として受ける
- いきなり確定登録せず、`AI 整理後候補一覧` を経由する
- 初期の AI は `ノンストップ自動確定` ではなく `提案 + 人の GO`
- 図では `ユーザー` actor から矢印が出ている箇所を人の操作点とする
- 紫系の `自動処理` は AI / job が進める箇所とする
- TODO 化と予定化は分けて考える
- `1 タスクから複数予定` を許容する
- 横断ダッシュボードは、最終的な見える化の集約点とする

## 画面の主な責務

### 1. 横断ダッシュボード

- 全データの流入と現在地を見える化する
- TODO、予定、整理候補、昇格済みアーカイブを追えるようにする
- MVP ではガント表示もここに含める

### 2. 書き入れ口 / 作成口

- Web 手入力の最小入口
- 手で思いつきを入れる最短導線

### 3. 管理画面

- 分類タグマスタ
- Codex プロンプトテンプレート
- 入口ごとの設定

### 4. 実績 / 履歴参照

- P0 では優先度は低い
- ただし将来、昇格の履歴や予定実績の参照先になる

## P0 以後に広げるもの

- AI の即確定自動化
- ゆるい重複束ね
- キャパ管理
- 外部協力者向け権限の本実装
