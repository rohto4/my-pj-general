# P0 タグマスタ仕様

作成日: 2026-07-10

## 目的

P0 の確認待ちキュー、入口 import、ガント、管理画面で使うタグの最小マスタを定義する。

タグは AI が候補付けするが、P0 ではユーザー確認待ちを必ず挟む。タグの自動付与は判断補助であり、GO の根拠として単独では使わない。

## P0 タグ種別

| 種別 | 例 | 用途 |
| --- | --- | --- |
| source | `slack`, `memo-ideas`, `knowledge-vault`, `inbox`, `misskey`, `manual` | 入口由来を示す |
| kind | `todo`, `idea`, `consideration`, `concern`, `schedule` | GO 後の作成先を判断する |
| workflow | `review`, `intake`, `p0`, `imported`, `gantt` | P0 内の処理状態を示す |
| domain | `role`, `permission`, `research`, `openproject` | 内容分類を示す |

## 初期タグ

```text
intake
review
knowledge-vault
inbox
slack
memo-ideas
gantt
schedule
role
codex
manual
imported
todo
idea
consideration
concern
```

## P0 管理画面で見る項目

| 項目 | P0 動作 |
| --- | --- |
| タグ名 | SQLite `tags.name` から表示する |
| カテゴリ | P0 では `general` を初期値にし、後続で分類する |
| 色 | P0 ではブルー系を基本にする |
| 表示 / 非表示 | P0 ではDB項目を持つが、UI上の編集は後続でよい |

## AI とユーザーの境界

- AI はタグ候補を付ける。
- ユーザーは確認待ちキューでタグの妥当性を見る。
- P0 ではタグ編集UIは最小表示に留める。
- P0 完了後、よく使うタグ、誤付与が多いタグ、source 固有タグを見てマスタを整理する。

## 実装対応

- SQLite: `tags`, `candidate_tags`
- UI: 管理画面 `タグマスタ`
- API: `/api/bootstrap`
