# AI レビュー用ブリーフ 2026-06-23

## 目的

このファイルは、別の AI に現在の検討状況を引き継ぎ、同じ論点を再発明せずにレビューや追加検討を依頼するための要約である。

## この PJ の前提

- PJ 名: `pj-general`
- 正本ルート: `G:\devwork\pj-general`
- 横断ナレッジ: `G:\knowledge-vault`
- 日本語で進行
- UTF-8 で読み書き
- この PJ は当面 `Codex 専用`
- まだ要件定義前フェーズなので、仕様断定より情報設計、運用設計、比較材料整備を優先する

## 作ろうとしているもの

個人の予定、個人タスク、組織タスク、協力者タスク、やりたいこと、判断記録、知識を一元管理する Web サイト。

特に重視している価値:
- 雑なアイデアを入口で受ける
- AI で分類、補完、タスク化する
- Google Calendar までつなげる
- 複数人、複数タスク前提で進行とキャパを見える化する
- Slack と knowledge-vault を外部入口として扱う
- Codex で新規 PJ を始める時の初期プロンプト、フォルダ設計、テンプレート選定を半自動化する

## 現時点で固まっている主要判断

### 1. 入口は自前実装

- OSS をそのまま UI として採用するのではなく、入口は独自実装する
- UI 基盤は `shadcn/ui` が有力
- 理由は、Open Code で AI が編集しやすく、独自の入口体験を作りやすいから

### 2. OSS は役割分担して借りる

- `Plane`
  - 入口の情報設計
  - アイデアから実行への導線
  - モダンな PM 体験の参照先
- `OpenProject`
  - ガント
  - 横断計画
  - タスクと計画の一体構造の参照先
- `Leantime`
  - TODO / タスクリストの軽さ
  - `ideas -> todos -> gantt` の流れ
  - 書き入れ口に近い体験設計の補助参照先

補足:
- `Redmine` は古さの観点で本線候補から外した
- `Backlog` は OSS ではない
- `OpenProject` の `Team planner` は Enterprise add-on なので、構造参照として扱う

### 3. 4 つの窓口に分ける

- 横断ダッシュボード
- 上位管理者用の管理画面
- 書き入れ口 / 作成口
- 実績 / 履歴参照

### 4. 外部入口を扱う

- Slack を入口にする
- knowledge-vault を入口にする
- 各 1 時間ごとに自分の投稿を回収する
- AI が次のどれかに自動分別する
  - タスク
  - スケジュール
  - 検討事項
  - 気になっている事

## 今の推奨技術スタック

- Web: `Next.js` App Router
- UI: `shadcn/ui`
- API: `Hono`
- DB: `PostgreSQL`
- ORM / query: `Drizzle ORM`
- Auth: `Better Auth`
- Queue: `BullMQ`
- Queue backend: `Redis`
- Form: `React Hook Form`

判断理由の要点:
- `Next.js`: 2026-06-23 時点でも土台として最も厚い
- `shadcn/ui`: Open Code / AI-Ready
- `Hono`: 薄く explicit で AI が壊しにくい
- `Drizzle`: SQL に近く、後から読みやすい
- `Better Auth`: AI resources や MCP があり相性が良い
- `BullMQ`: 定期回収、AI 分別、通知、再試行に素直

補足:
- `TanStack Start` と `TanStack Form` は熱いが、2026-06-23 時点では主軸採用を保留
- `Fastify` と `Prisma` は依然として有力な代替

## いまの構成イメージ

- `apps/web`
  - 書き入れ口
  - 横断ダッシュボード
  - 実績 / 履歴参照
- `apps/admin`
  - 上位管理者用の管理画面
- `services/api`
  - Hono ベース API
- `packages/domain`
  - アイデア、タスク、予定、ロール等
- `packages/ui`
  - shadcn/ui ベース共通部品
- `packages/db`
  - Drizzle schema / migration / query
- `packages/integrations`
  - Slack / Google Calendar / knowledge-vault
- `workers/sync`
  - 定期回収
- `workers/ai`
  - AI 分別
- `workers/notify`
  - 通知、再試行

## 現時点の主要課題

### A. ドメイン境界

- `アイデアカード` と `タスク` を別 object にするか
- `予定`、`検討事項`、`気になっている事` を同一系列で扱うか
- 1 件の入力が複数 object に分かれる時のルールをどうするか

### B. 正本と同期

- 正本 object が何かを固定する必要がある
- Google Calendar、Slack、knowledge-vault との同期方向を決める必要がある
- 重複登録や再試行時の冪等性が必要

### C. AI 分別フロー

- 即確定にするか
- 下書き登録にするか
- 人レビュー必須にするか
- AI が出した分類理由や補足をどこまで残すか

### D. 権限

- 自分、外部協力者、将来の社内メンバーの 3 段階を最低限考える
- 閲覧権限と操作権限を分ける必要がある
- ダッシュボード閲覧と編集権限を分離する必要がある

### E. Next.js と Hono の責務境界

- `Next.js` に業務ロジックを漏らしすぎないこと
- `Hono` を Day 1 から切るか
- 初期だけ Route Handlers を併用するか

### F. OSS 借用の仕方

- OpenProject / Leantime を「製品採用」ではなく「構造 / 体験 / 一部ビュー参照」として扱う
- view model と domain model の変換層が必要になる可能性が高い

## 特にレビューしてほしい論点

1. `アイデア -> タスク / 予定 / 検討事項` への昇格モデルの切り方
2. `Next.js + Hono + Drizzle` の責務分離の妥当性
3. `Google Calendar`、`Slack`、`knowledge-vault` を含む正本設計
4. 最小ロールモデルの切り方
5. `OpenProject` と `Leantime` の借用粒度の切り方

## 望ましいレビューの仕方

- 現時点の判断を全部ひっくり返すのではなく、破綻しやすい点を指摘してほしい
- 代替案を出す場合は、どの課題に対して有利かを明示してほしい
- 実装を楽にするだけでなく、将来の大型化と AI 併走のしやすさも見てほしい
