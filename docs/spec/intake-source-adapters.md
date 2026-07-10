# P0 入口別 adapter 仕様

作成日: 2026-07-09

## 目的

この文書は、P0 の 4 入口である `web 手入力`、`Slack`、`Misskey`、`knowledge-vault` を `Raw入口イベント` へ変換する adapter の責務を定義する。

詳細な本認証、本 AI、外部 DB サーバはここでは確定しない。2026-07-10 時点の P0 本デモでは、SQLite と最小 API で入口データを確認待ちキューへ流す。

## 共通責務

すべての adapter は、入口固有 payload をそのまま業務 object にしない。

共通の流れは次とする。

```text
source payload
-> adapter
-> Raw入口イベント
-> 正規化イベント
-> AI整理結果
-> 確認待ちキュー
-> ユーザーGO
-> 業務object
```

adapter が作るのは `Raw入口イベント` までとする。

## adapter 別方針

| Adapter | P0 薄く実装 1 版 | P0 完了時点の方向 |
| --- | --- | --- |
| Web manual | drawer から `/api/candidates` へ登録し、SQLite に保存する | 最初の本線入口として維持する |
| Slack | connector / 手動 import payload を `/api/import/slack` へ渡す。対象は `memo-ideas` チャンネルに限定 | Slack API / event / polling のどれで取るかを後続確定する |
| Misskey | mock data で確認。note payload 形を想定 | webhook 受信または polling を後続確定する |
| knowledge-vault | `/api/import/knowledge-vault` で `inbox`、`records`、`tasks`、`memory` の Markdown を `KV-*` 候補として取り込む | 対象範囲内はいったん全件対象にし、差分検知、更新時刻、content hash を使って取り込む |

## Web manual adapter

### 入力

- タイトル
- 本文
- URL
- 任意タグ
- 予定化したいかどうかの緩い指定

### Raw入口イベント

| Field | 値 |
| --- | --- |
| `source_type` | `web` |
| `source_ref` | 画面生成 ID |
| `payload` | 入力フォームの JSON |
| `source_url` | 入力 URL がある場合 |
| `occurred_at` | 入力時刻 |

## Slack adapter

### P0 暫定範囲

- 特定チャンネルを対象にする。
- チャンネル名は `memo-ideas`。
- URL は `https://unibell4-dev.slack.com/archives/C0BG4TCPAUD`。
- 全ワークスペース、全チャンネル、全DMは対象外。
- 抽出対象は、やりたいこと、困っていること、タスクっぽいこと。

### Raw入口イベント

| Field | 値 |
| --- | --- |
| `source_type` | `slack` |
| `source_ref` | channel id + ts |
| `payload` | message text、thread 情報、reaction 情報の snapshot |
| `source_url` | Slack permalink が取れる場合 |
| `occurred_at` | message ts |

### 初期画面で見せる項目

- チャンネル名
- 投稿者
- 投稿日時
- 本文抜粋
- thread / reaction の有無
- AI 整理結果

## Misskey adapter

### P0 暫定範囲

- note payload を Raw として保存できる形を想定する。
- 実接続方式は後続で決める。

### Raw入口イベント

| Field | 値 |
| --- | --- |
| `source_type` | `misskey` |
| `source_ref` | note id |
| `payload` | note data snapshot |
| `source_url` | note URL が作れる場合 |
| `occurred_at` | note createdAt |

## knowledge-vault adapter

### P0 暫定範囲

優先対象は次。

```text
G:\knowledge-vault\records\
G:\knowledge-vault\inbox\
G:\knowledge-vault\memory\l1-triggers.md
G:\knowledge-vault\memory\l2-models\
G:\knowledge-vault\tasks\active\
G:\knowledge-vault\tasks\handoff\
```

詳細は `docs/candi-ref/knowledge-vault-current-structure-for-intake.md` を参照する。

対象範囲内は、P0 では日付やファイル名で細かく絞らず、いったん全件を対象にする。

### 抽出対象

- やりたいこと
- 困っていること
- タスクっぽいこと
- 検討したこと
- 知見の種
- 後で判断したいこと
- 後で調べたいこと
- 次アクションや handoff に相当すること

### Raw入口イベント

| Field | 値 |
| --- | --- |
| `source_type` | `knowledge_vault` |
| `source_ref` | vault relative path + heading / block id 相当 |
| `payload` | file path、mtime、heading、excerpt、周辺文脈 |
| `source_url` | ローカル path または Obsidian link 相当 |
| `occurred_at` | file mtime または文中日付 |
| `content_hash` | excerpt または block の hash |

## P0 本デモ状態の扱い

- Web manual は画面から実入力し、SQLite に永続化する。
- Slack は `memo-ideas` connector の読み取りを確認済み。現時点で対象投稿はないため、P0では import payload 経路を用意する。
- Misskey は mock data のまま後続扱いにする。
- knowledge-vault はローカル scan を実装済み。検証時点で10件を `KV-*` 候補として取り込んだ。
- すべての AI 整理結果は確認待ちキューに入り、自動 GO はしない。

## P0 では決めないこと

- アプリ本体へ Slack API 認証を持たせる方式。
- Misskey の受信方式。
- knowledge-vault の差分検知実装の詳細。
- 自動 dedupe の厳密条件。
- 部分自動確定の条件。

## 関連文書

- `docs/spec/intake-unified-event-model.md`
- `docs/spec/ai-assisted-registration-flow.md`
- `docs/candi-ref/knowledge-vault-current-structure-for-intake.md`
- `docs/candi-ref/ui-reference-sources-for-initial-prototype.md`
