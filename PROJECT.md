# PJ-General Project Context

## PJ の目的

この PJ は、個人のスケジュール管理、個人タスク管理、社員や協力者を含むチームタスク管理、やりたいことの蓄積、判断記録、知識管理を一元化するサイトを作るための拠点である。

要件定義前フェーズでは、仕様を早く固定することよりも、情報設計、運用設計、比較材料、将来の統合設計を整えることを優先する。

## PROJECT.md の責務

`PROJECT.md` は、PJ 固有の目的、スコープ、正本関係、恒久的な構造、採用済みの重要判断を示す最重要ファイルである。

次の内容は `PROJECT.md` に置かない。

- タスク一覧、進捗、次走テーマ
- セッション履歴、handoff、作業ログ
- 判断材料の生ログ、参照元一覧、調査メモ
- 一時的な TODO、会話中の未整理メモ

置き場所は次のように分ける。

- タスク、進捗、完了記録: `docs/imp/*`
- セッション履歴、handoff: `docs/diary/*`
- 候補、比較、参照元、未採用案: `docs/candi-ref/*` または `docs/setting/*`
- 採用判断の根拠、設計判断: `docs/arch/*`、`docs/spec/*`、`docs/product/*`、`tech-stack.md`

## 作業入口

- 毎チャット共通の起動前提: `AGENTS.md`
- 技術スタックと実務ツールの正本: `tech-stack.md`
- ユーザー確認・操作: `docs/imp/user-tasks.md`
- ユーザー判断待ち: `docs/imp/user-judge.md`
- 実装待ち: `docs/imp/imp-tasks.md`
- 実装方針: `docs/imp/imp-plan.md`
- 完了記録: `docs/imp/imp-comp.md`

## 文書管理の正本関係

- PJ 全体の実行ルールは `AGENTS.md` を正本にする。
- PJ の目的、入口、構造、採用済みの重要判断は `PROJECT.md` を正本にする。
- 技術スタックと実務ツールは `tech-stack.md` を正本にする。
- docs 配下の置き場所、相互更新ルール、タイミング別更新判断表は `docs/guide/docs-management-rules.md` を正本にする。
- docs 配下の入口一覧は `docs/README.md` とし、詳細ルールを重複させない。

## 新PJへの引き継ぎ

- 新PJへこの運用を移す場合は、`docs/guide/docs-management-rules.md` の「新PJへ引き継ぐ最小ルールセット」を基準にする。
- `AGENTS.md` / `PROJECT.md` だけでなく、`docs/guide/docs-management-rules.md`、`docs/guide/docs-management-matrix-result-diagram.md`、`docs/README.md`、`docs/imp/*` の最小セット、`.agents/README.md` も AI 設定・運用関連ファイルとして引き継ぐ。
- `G:\knowledge-vault\knowledge-vault-write-policy.md` は横断ナレッジ更新判断の中央正本として参照し、PJ 側へ重複コピーしない。

## 初期ディレクトリ構造

```text
G:\devwork\pj-general
├── AGENTS.md
├── PROJECT.md
├── README.md
├── .agents\skills\
├── commands\
├── apps\
├── services\
├── packages\
├── workers\
├── plugins\
├── infra\
├── scripts\
├── tests\
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

## PJ 固有の決定事項

- この PJ の開発運用は当面 Codex 専用として扱う。
- Codex 専用運用土台の参照元は `aaif-goose/goose` を第一候補とする。
- MCP 実装や CLI 操作の参照元は `PrefectHQ/fastmcp` を第一候補とする。
- MCP 参照サーバの把握には `modelcontextprotocol/servers` を使う。
- `awesome-mcp-servers` は巨大索引として有用だが、この PJ に直接コピーして使う土台としては優先しない。
