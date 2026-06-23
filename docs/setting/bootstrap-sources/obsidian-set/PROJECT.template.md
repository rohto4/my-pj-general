# obsidian-set Project Context

## 目的

この PJ は、次の 3 つの正本を設計、更新、検証するための拠点。

1. `G:\knowledge-vault` の日常運用ルール
2. `G:\my-LLMwiki` の週次製本ルール
3. 両者をつなぐ compile 方針、frontmatter、review 手順

## 採用方針

- `G:\knowledge-vault` を日常記録の正本とする
- `G:\my-LLMwiki` を knowledge-vault から定期生成する製本ビューとする
- Obsidian 内での二重記録を避ける
- タスク管理は外部ツールを正本にする

## 情報配置

| Path | 役割 |
|---|---|
| `docs/guide/` | 採用済み運用ガイド |
| `docs/spec/` | frontmatter、compile、weekly batch 仕様 |
| `docs/condi-ref/` | 比較案、未採用案、条件付き参考資料 |
| `docs/imp/` | 実装メモ、移行作業記録 |

## 重要な関係

- `obsidian-set` は運用ルールの拠点
- `knowledge-vault` は記録、根拠、判断、知識、LLM想起の正本
- `my-LLMwiki` は knowledge-vault から作る compiled wiki

## GitHub 運用メモ

- `my-LLMwiki` が進んだら `rohto4` アカウントで `rohto4/my-LLMwiki.git` に定期的に commit / push する
- `obsidian-set` など他 repo も、`rohto4` アカウントでの定期的な commit / push を忘れない

## 更新時の原則

- まず `knowledge-vault` の保存先ルールを決める
- 次に `my-LLMwiki` の compile 先と page 種別を決める
- 最後に batch と lint を決める
