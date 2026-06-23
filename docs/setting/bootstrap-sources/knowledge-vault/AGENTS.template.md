# knowledge-vault Agent Instructions

## 最優先ルール

1. 日本語で対応する。
2. UTF-8 で読み書きする。
3. この vault は日常運用の正本として扱う。
4. `G:\my-LLMwiki` はこの vault から定期生成する派生物として扱う。
5. 同じ内容を `knowledge-vault` と `my-LLMwiki` に手動で二重記録しない。
6. `sources/`, `records/`, `knowledge/` を正本、`memory/` を索引、`wiki/` を compile 済みビューとして扱う。
7. 外部タスク管理ツールが正本のタスク状態を持つ。ここでは作業記録と判断履歴を扱う。

## 役割

| Path | 役割 |
|---|---|
| `sources/` | 根拠資料の正本 |
| `records/` | 作業記録、handoff、セッション履歴 |
| `knowledge/` | 再利用知識の正本 |
| `memory/` | LLM用の想起入口 |
| `prompts/` | 重要な依頼文と回答要約 |
| `wiki/` | vault 内で見る compile 済みビュー |
| `tasks/` | 旧構成の履歴。段階的に `records/` へ移行する |

## 書き込み判断

1. 実施履歴は `records/`
2. 根拠は `sources/`
3. 再利用知識は `knowledge/`
4. 想起入口は `memory/`
5. compile 結果は `wiki/` と `G:\my-LLMwiki`
