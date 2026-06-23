# knowledge-vault Project Context

## 目的

この vault は、日常の記録、根拠、判断、知識、LLM想起を残す正本。

加えて、週次または節目に `G:\my-LLMwiki` を生成する source of truth として扱う。

## 運用方針

- 正本はローカル Markdown
- `records/`, `sources/`, `knowledge/` を中心に運用する
- `wiki/` は vault 内の compile 済みビュー
- `G:\my-LLMwiki` は外向きの製本ビュー
- 手修正が必要な場合はまず正本側を更新する

## 目標構成

```text
inbox/
sources/
records/
knowledge/
memory/
prompts/
wiki/
data/
scripts/
templates/
attachments/
```

## 移行方針

- 既存 `tasks/` はすぐに破壊しない
- 新規記録は `records/` に寄せる
- `tasks/` は legacy として段階移行する
