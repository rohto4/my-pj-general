# 推奨 OSS 組み合わせと自前実装スタック

## 目的

現時点の判断で、`pj-general` をどういう構成で組むのが最も自然かを整理する。

この文書は、要件確定前の推奨構成であり、実装確定版ではない。

## 結論

今のおすすめは、`入口は完全自前`、`計画系ビューは OSS の思想と一部実装を借りる`、`業務オブジェクトと権限は自前` という構成である。

役割分担は次の通り。

- `Plane`
  - 入口の情報設計
  - モダンな PM 体験
  - アイデアから実行への導線
- `OpenProject`
  - ガント
  - 横断計画
  - タスクと計画の一体構造
- `Leantime`
  - TODO / タスクリストの軽さ
  - `ideas -> todos -> gantt` の流れ
  - 書き入れ口に近い体験

重要なのは、最初から 3 つの OSS をそのまま統合運用することではない。

現時点の本線は、自前アプリの中にこれらの思想や一部ビュー実装を取り込む構成である。

## プロダクト全体の推奨構成

### 自前で持つ中核

- アイデア入力
- Slack / knowledge-vault の回収
- AI 自動分別
- アイデアからタスクへの昇格
- Google Calendar 登録導線
- ロールと公開範囲の制御
- Codex プロジェクト開始支援

### OSS から主に借りる部分

- ガントチャートの構造と見せ方
- TODO / タスクリストの見せ方
- 横断ダッシュボードの情報整理
- 人員計画ビューの発想

## 画面ごとの推奨組み合わせ

### 1. 書き入れ口 / 作成口

- 自前実装
- 参照先は `Plane` と `Leantime`

理由:
- 差別化要因がここにあるから
- Slack / knowledge-vault / AI 分別は自前でつないだ方が自然だから

### 2. 横断ダッシュボード

- 自前実装
- 構造参照は `OpenProject`
- 情報整理の補助参照は `Plane`

理由:
- ロールごとの可視範囲制御を自前で持ちたいから
- ただし複数人、複数タスク、複数 PJ の見せ方は `OpenProject` が強いから

### 3. TODO / タスクリスト

- 自前実装を前提
- 体験参照は `Leantime`
- 属性や横断整合は `OpenProject` を参照

理由:
- デザインが重要で、入口に近い軽さが必要だから

### 4. ガントチャート

- 自前の業務モデルに載せる
- 表示構造の主参照は `OpenProject`
- 軽量な近接体験は `Leantime` を補助参照

理由:
- ガントは結合度が高く、タスクと別製品として完全分離しにくいから
- ただし `OpenProject` の思想は強くても、そのまま製品組み込みとは限らないから

## 自前実装側の推奨技術スタック

### フロントエンド

- 第一候補: `Next.js` App Router
- UI 基盤: `shadcn/ui`
- スタイリング: `Tailwind CSS`

理由:
- `Next.js` 公式 docs では App Router を中心に、`Route Handlers`、`Backend for Frontend`、`Authentication`、`Testing` までガイドが揃っている
- `shadcn/ui` は「コンポーネントライブラリを使う」のではなく「自分のコードとして持つ」思想で、Open Code と AI-Ready を前面に出している
- 今回は入口 UI を自前で磨く必要があるため、編集しやすい UI 基盤が向く

### バックエンド API

- 第一候補: `Fastify`
- 代替案: MVP だけ `Next.js Route Handlers` で開始

推奨判断:
- 戦略上は `Fastify` を本命にした方がよい

理由:
- この PJ は、タスク、予定、権限、外部同期、AI 分別、定期回収が絡む
- 将来的に `web` と `worker` と `api` の責務分離が必要になる可能性が高い
- `Next.js` にすべての業務ロジックを抱え込むより、API 境界を持った方が大型化に耐えやすい

### データベース

- 第一候補: `PostgreSQL`
- ORM 第一候補: `Prisma ORM`

理由:
- 中核オブジェクトが多く、リレーショナル整合を強く持ちたいから
- `Prisma ORM` は TypeScript と相性がよく、型安全なアクセスを前面に出している
- 初期は検索も PostgreSQL の範囲で始めやすい

### 認証・認可

- 第一候補: `Better Auth`

理由:
- TypeScript 向けで framework-agnostic
- docs 上で organization / access control、multi-session、plugin 拡張が揃っている
- AI リソースや MCP も用意されていて、この PJ の運用文脈と相性がよい

注意:
- 認可の最終モデルは自前のロール設計で握る
- `Better Auth` は土台候補であり、権限制御そのものを丸投げする前提ではない

### 非同期ジョブ

- 第一候補: `BullMQ`
- 補助基盤: `Redis`

理由:
- 1 時間ごとの Slack / knowledge-vault 回収
- AI 分別ジョブ
- Calendar 登録準備
- 通知や再試行

こうした処理を同期リクエストから切り離す前提と相性がよい

### ワーカー

- `workers/` に独立責務で置く

想定する worker:
- Slack 回収
- knowledge-vault 回収
- AI 分別
- Google Calendar 連携
- リマインド / 通知

## 今のおすすめ構成をモノレポに落とすと

### `apps/`

- `apps/web`
  - 書き入れ口
  - 横断ダッシュボード
  - 実績・履歴参照
- `apps/admin`
  - 上位管理者用の管理画面

### `services/`

- `services/api`
  - 業務 API
  - 認証連携
  - 権限評価
  - タスク、予定、履歴の中核処理

### `packages/`

- `packages/domain`
  - アイデア、タスク、予定、ロールなどのドメイン
- `packages/ui`
  - `shadcn/ui` ベースの共通部品
- `packages/integrations`
  - Slack、Google Calendar、knowledge-vault 連携

### `workers/`

- `workers/sync`
  - 定期回収
- `workers/ai`
  - AI 分別
- `workers/notify`
  - 通知、再試行、リマインド

## まだ検討が必要な部分

### 1. `apps/web` と `apps/admin` を最初から分けるか

候補:
- 最初から分ける
- 最初は 1 つの Next.js アプリで route group 分離する

現時点のおすすめ:
- 最初は 1 つの `Next.js` アプリで始め、権限とルートで分ける

理由:
- 初期の画面と権限設計を早く詰められるから
- ただし repo 構造は分離しやすく保つ

### 2. API を最初から `Fastify` 分離するか

候補:
- 最初から `services/api` を立てる
- MVP だけ `Next.js Route Handlers` で始める

現時点のおすすめ:
- 境界を意識して `services/api` 前提で設計する
- ただし初期速度優先なら、最初の数画面だけ `Route Handlers` を併用してよい

### 3. 検索基盤を PostgreSQL だけで始めるか

候補:
- PostgreSQL の全文検索で始める
- 早期から専用検索基盤を入れる

現時点のおすすめ:
- まず PostgreSQL で始める

理由:
- 今は要件抽出フェーズで、検索要求の密度がまだ読めないから

### 4. フォーム管理を何で統一するか

候補:
- `React Hook Form`
- `TanStack Form`

現時点の判断:
- 未固定

理由:
- `shadcn/ui` 側は両方の導線を持っている
- 実際の入力密度とバリデーション要件を見て決めた方がよい

## いまの推奨スタック

- UI: `Next.js` + `shadcn/ui` + `Tailwind CSS`
- API: `Fastify`
- DB: `PostgreSQL`
- ORM: `Prisma ORM`
- Auth: `Better Auth`
- Queue: `BullMQ`
- Cache / queue backend: `Redis`

## 次に決めるべきこと

1. `apps/web` と `apps/admin` を初期から分けるか
2. `Fastify` を Day 1 から立てるか
3. フォーム基盤を `React Hook Form` と `TanStack Form` のどちらにするか
4. Google Calendar 連携を初期はプロンプト出力に留めるか、直接登録まで入れるか
