# knowledge-vault 現構成と P0 取り込み対象メモ

## 目的

この文書は、`pj-general` の P0 で `G:\knowledge-vault` を入口として扱う際に、どの範囲を暫定取り込み対象にするかを判断するための参考資料である。

作成時点の構成をもとにしているため、将来 `knowledge-vault` 側の構造が変わった場合は再確認する。

## ユーザー判断

- Slack は特定チャンネルを参照対象にする。
- Slack チャンネルは `memo-ideas`。
- Slack URL は `https://unibell4-dev.slack.com/archives/C0BG4TCPAUD`。
- knowledge-vault は diary 系を基本参照対象にする。
- memory は L2 までを参照対象にする。
- 対象内容は、やりたいこと、困っていること、タスクっぽいこと。
- `inbox/` は未整理の検討、知見の種、後で昇格すべき材料が入る可能性があるため対象にする。
- knowledge-vault は対象範囲内をいったん全件対象にする。
- P0 薄く実装 1 版では、AI 整理結果はすべて確認待ちにする。

## 現在の主要構成

| Path | 現在の役割 | P0 取り込み判断 | ひとことコメント |
| --- | --- | --- | --- |
| `records/` | 作業記録、handoff、セッション履歴 | 優先対象 | 現在の vault では diary 系に最も近い正本。次アクションや判断の種が出やすい。 |
| `inbox/` | 未整理情報の一時置き場 | 優先対象 | 正本ではないが、検討したこと、知見の種、後で昇格すべき材料が入る可能性がある。P0 では確認待ちキューへ出して人が判断する。 |
| `memory/l1-triggers.md` | 常時読む短いトリガーとリンク | 参照対象 | LLM 想起入口。本文は薄いが、回収候補の発見に使える。 |
| `memory/l2-models/` | 未確定の理解モデル、仮説、違和感 | 参照対象 | 困っていること、検討事項、まだ固まっていないやりたいことが出やすい。 |
| `tasks/active/` | legacy の active task note | 参照対象 | legacy だが、移行前タスクが残る可能性がある。 |
| `tasks/handoff/` | legacy の handoff note | 参照対象 | 引き継ぎ文脈から未完タスクを拾うために見る。 |
| `tasks/done/` | legacy の完了 task note | 原則対象外 | 完了済み中心。参照はできるが、初期回収ではノイズになりやすい。 |
| `knowledge/` | 整理済みナレッジの正本 | 原則対象外 | タスク回収ではなく、AI 整理の背景知識として必要時に見る。 |
| `knowledge/dev/` | 開発ノウハウ | 原則対象外 | 再利用知識なので、やりたいこと抽出の主対象にはしない。 |
| `knowledge/ai/` | AI / LLM / agent 知見 | 原則対象外 | 同上。必要なら文脈補助に使う。 |
| `knowledge/decisions/` | 判断済み事項と理由 | 原則対象外 | 決定事項の正本であり、未整理タスク抽出には向きにくい。 |
| `sources/` | 根拠資料の正本 | 対象外 | 根拠資料であり、タスク候補の入口ではない。 |
| `wiki/` | compile 済みビュー | 対象外 | 派生ビューなので、重複回収を避けるため対象外。 |
| `prompts/` | 重要な依頼文と回答要約 | 保留 | 今後増えるならやりたいこと抽出に有用な可能性があるが、P0 初期では対象外寄り。 |
| `templates/` | テンプレート | 対象外 | タスク抽出対象ではない。 |
| `scripts/` | vault 補助スクリプト | 対象外 | 運用補助。タスク抽出対象ではない。 |
| `attachments/` | 添付ファイル | 対象外 | 本文抽出の主対象ではない。リンク先として保持する程度。 |
| `data/vault.sqlite` | index / data store | 対象外 | 実装時に検索補助として使う可能性はあるが、P0 の入力本文にはしない。 |

## P0 暫定スキャン範囲

P0 薄く実装 1 版の mock / scan 設計では、次を優先する。

```text
G:\knowledge-vault\records\
G:\knowledge-vault\inbox\
G:\knowledge-vault\memory\l1-triggers.md
G:\knowledge-vault\memory\l2-models\
G:\knowledge-vault\tasks\active\
G:\knowledge-vault\tasks\handoff\
```

`records/` を diary 系の主対象として扱い、`tasks/` は legacy 参照として扱う。
対象範囲内は、P0 では日付やファイル名で細かく絞らず、いったん全件対象にする。

## 抽出する内容

AI 整理対象にするのは、次のいずれかに該当する記述。

- やりたいこと
- 困っていること
- タスクっぽいこと
- 検討したこと
- 知見の種
- 後で判断したいこと
- 後で調べたいこと
- 次アクションや handoff に相当すること

抽出しないものは次。

- 整理済みナレッジ本文の再取り込み
- 完了済み作業だけの記録
- テンプレート本文
- compile 済み wiki の重複内容
- scripts や設定ファイルの本文
- secret、token、Cookie、未公開認証情報、個人情報の不用意な転記

## 画面上の見せ方

knowledge-vault 由来の候補は、確認待ちキューで次を出す。

| 表示 | 内容 |
| --- | --- |
| 入口 | `knowledge-vault` |
| source label | `records` / `inbox` / `memory L1` / `memory L2` / `legacy tasks` など |
| source path | vault 内 path |
| excerpt | 抽出元の短い抜粋 |
| AI summary | やりたいこと、困りごと、タスク候補としての要約 |
| candidate kind | `idea` / `consideration` / `concern` / `todo` / `schedule_candidate` |
| actions | `GO` / `編集してGO` / `保留` / `不要` |

## 後でユーザーが判断する点

- P0 以後に `records/` / `inbox/` 配下を日付やファイル名で絞るか。
- `prompts/` を P0 完了後に対象へ入れるか。
- `knowledge/` を完全に対象外にするか、明示タグ付きのものだけ取り込むか。
- `memory/l3-summaries/` を、重複を許容してでも確認待ちキューへ出すか。

## 参照した vault 側ファイル

- `G:\knowledge-vault\README.md`
- `G:\knowledge-vault\records\README.md`
- `G:\knowledge-vault\memory\README.md`
- `G:\knowledge-vault\tasks\README.md`
- `G:\knowledge-vault\knowledge\README.md`
- `G:\knowledge-vault\knowledge-vault-write-policy.md`
