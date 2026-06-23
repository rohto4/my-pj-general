# obsidian-set Agent Instructions

## 最優先ルール

1. 日本語で対応する。
2. UTF-8 で読み書きする。
3. この PJ は `G:\knowledge-vault` と `G:\my-LLMwiki` の運用設計拠点として扱う。
4. `G:\knowledge-vault` は日常運用の正本、`G:\my-LLMwiki` は定期コンパイルされる製本ビューとして扱う。
5. `G:\my-LLMwiki` を日常の直接記録先にしない。
6. タスク管理は外部ツールを正本にし、この PJ と vault は記録、根拠、判断、知識、想起に集中する。
7. ルール追加時は `AGENTS.md` に詰め込まず、`PROJECT.md` または `docs/guide/`、`docs/spec/` に分ける。

## 読み込み順

1. `AGENTS.md`
2. `PROJECT.md`
3. `docs/README.md`
4. 必要な `docs/guide/*.md`
5. 必要な `docs/spec/*.md`
6. 必要な `docs/condi-ref/*.md`

## 運用の芯

- 日常の記録、根拠、セッション、判断は `G:\knowledge-vault` に残す。
- `G:\my-LLMwiki` は週次または節目に compile する。
- compile では Raw と Wiki を分ける。
- 同じ内容を `knowledge-vault` と `my-LLMwiki` に手動で二重記録しない。

## このPJの役割

- 運用ルールの正本
- compile 方針、frontmatter、weekly review、questions 蓄積方針の整理拠点
- 未採用案の比較と廃止判断
