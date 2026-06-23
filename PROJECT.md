# PJ-General Project Context

## 仮目的

この PJ は、個人のスケジュール管理、個人タスク管理、社員や協力者を含むチームタスク管理、やりたいことの蓄積、判断記録、知識管理を一元化するサイトを作るための拠点。

現時点では要件定義前フェーズとして、次を優先する。

1. 大規模PJ向けの地盤整備
2. 既存資産からのテンプレート / skills / commands の流用
3. 情報設計とディレクトリ設計の確立
4. 候補 OSS の比較準備
5. 統合戦略の検討準備

## 今回の到達目標

- モノレポ前提のルート構造を作る
- agent 指示、project 文脈、docs 運用を初期化する
- `obsidian-set` / `knowledge-vault` / `my-LLMwiki` の有用テンプレートを取り込む
- Codex 専用運用土台として参照する高スター repo を clone し、必要部分を取り込む
- 次走で OSS 選定と統合計画に入れる状態を作る

## 作業入口

- 毎チャット共通の起動前提: `chat-init.md`
- ユーザー確認・操作: `docs/imp/user-tasks.md`
- ユーザー判断待ち: `docs/imp/user-judge.md`
- 実装待ち: `docs/imp/imp-tasks.md`
- 実装方針: `docs/imp/imp-plan.md`
- 完了記録: `docs/imp/imp-comp.md`

## `chat-init.md` の役割

- `chat-init.md` は、毎チャットの最初に読む共通初期化ファイル。
- ここには、読み込みのたびに有効な共通運用ルール、出力方針、更新方針だけを置く。
- 現状の検討結果や handoff は含めず、PJ の進行状態は `docs/diary/*` や `docs/imp/*` に置く。

## 初期ディレクトリ構造

```text
G:\devwork\pj-general
├── AGENTS.md
├── PROJECT.md
├── chat-init.md
├── README.md
├── .agents\skills\          # obsidian-set + fastmcp 由来 skill を流用
├── commands\                # obsidian-set 由来 command を流用
├── apps\                    # フロントエンド群
├── services\                # API / Auth / Sync / Gateway
├── packages\                # 共通ライブラリ / ドメイン / UI
├── workers\                 # バッチ / 非同期処理 / AI ジョブ
├── plugins\                 # 拡張モジュール
├── infra\                   # デプロイ / IaC / 監視 / 権限
├── scripts\                 # セットアップ / 開発補助
├── tests\                   # 統合テスト基盤
├── docs\
│   ├── guide\
│   ├── spec\
│   ├── candi-ref\
│   ├── imp\
│   ├── diary\
│   ├── setting\
│   ├── ops\
│   ├── product\
│   ├── arch\
│   ├── org\
│   └── data\
└── tmp\
```

## 構造の意図

- `apps` と `services` を分けることで、UI 統合とバックエンド分離の両方に対応する。
- `packages` にドメインと共通 UI を集約し、将来の複数フロントエンド展開に備える。
- `plugins` を独立させることで、候補 OSS の一部機能を段階導入しやすくする。
- `docs` を product / arch / data / ops / org に分割し、100 万行規模でも知識を迷子にしにくくする。

## 参照した流用元

- `G:\devwork\obsidian-set`
- `G:\devwork\tool-set`
- `G:\knowledge-vault`
- `G:\my-LLMwiki`
- `G:\devwork\clone-dir\aaif-goose-goose`
- `G:\devwork\clone-dir\PrefectHQ-fastmcp`
- `G:\devwork\clone-dir\modelcontextprotocol-servers`
- 参考記事: NocoBase ブログ「GitHubスター数トップ10のオープンソースプロジェクト管理ツール」
  - 記事公開: 2025-09-17
  - 記事最終更新: 2026-01-21

## 現時点の採用判断

- Codex 専用運用土台の参照元は `aaif-goose/goose` を第一候補とする。
- MCP 実装や CLI 操作の土台は `PrefectHQ/fastmcp` を第一候補とする。
- MCP 参照サーバの把握には `modelcontextprotocol/servers` を使う。
- `awesome-mcp-servers` は巨大索引として有用だが、この PJ に直接コピーして使う土台としては優先しない。

## 次走のテーマ

次は、候補 OSS の選定基準を確定し、引用・拡張に向いたプロジェクトの比較表と統合シナリオを作る。
