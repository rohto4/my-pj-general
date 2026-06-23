# knowledge-vault

日常の記録、根拠、判断、知識、LLM想起を残す本運用 vault。

## 最初に見るファイル

1. `AGENTS.md`
2. `PROJECT.md`
3. `records/README.md`
4. `knowledge/README.md`
5. `sources/README.md`
6. `wiki/README.md`

## 主要構成

```text
sources/     根拠資料の正本
records/     作業記録、handoff、セッション履歴
knowledge/   再利用知識の正本
memory/      LLM想起用の短い入口
prompts/     重要な依頼文と回答要約
wiki/        compile 済みビュー
```

## Compile

- vault 内 compile view: `wiki/`
- 製本出力先: `G:\my-LLMwiki`
- batch: `scripts/compile-llmwiki/weekly-compile-to-llmwiki.ps1`
