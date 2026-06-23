# 実務寄り + AI 友好性重視のスタック選定 2026-06

## 前提

この文書では、次の条件で技術選定を見直す。

- 不特定多数向けの見た目最適化は最優先にしない
- 実用性を最優先にする
- 最新の AI が読みやすく、編集しやすく、壊しにくい構成を優先する
- 2026-03 以降の温度感を踏まえる

## 結論

今のおすすめは次の構成。

- Web: `Next.js` App Router
- UI: `shadcn/ui`
- API: `Hono`
- DB: `PostgreSQL`
- ORM / query: `Drizzle ORM`
- Auth: `Better Auth`
- Queue: `BullMQ`
- Queue backend: `Redis`
- Form: `React Hook Form`

前回の「`Fastify` + `Prisma` も堅い」という判断は維持できるが、今回の評価軸では `Hono` と `Drizzle` の方が少し有利である。

## なぜこうなるか

### 1. `Next.js` はまだ本命

- 2026-06-23 時点の公式 docs は `App Router` を中心に構成されている
- docs には `AI Coding Agents` ガイドと `Next.js MCP Server` ガイドが見えている
- GitHub stars も大きく、エコシステム厚みがある

判断:
- 流行だけなら `TanStack Start` はかなり熱い
- ただし、2026-06-23 時点でも `TanStack Start` は `RC` 表記
- この PJ は要件が広く、途中で業務領域も膨らみやすいので、今は `Next.js` を主軸にした方が安全

### 2. `shadcn/ui` はそのまま有力

- 公式 docs では `Open Code` と `AI-Ready` を明確に打ち出している
- 「ライブラリを import する」のではなく、「自分のコンポーネントコードとして持つ」思想である
- 今回のような独自入口では、AI が直接 component code を読んで修正できるメリットが大きい

判断:
- UI を完全自前で育てる前提なら、今でも `shadcn/ui` が最有力

### 3. API は `Fastify` より `Hono` を推す

- `Hono` は Web Standards ベースで、小さく、単純で、multi-runtime
- 公式 docs に `LLM` セクションがある
- GitHub README でも `zero dependencies`、`Web Standard API`、`first-class TypeScript support` を強く出している

判断:
- AI は「暗黙の多い重いサーバフレームワーク」より、「薄くて explicit な HTTP 層」の方が壊しにくい
- その意味で、今回のような自前ドメイン中心の PJ では `Hono` の方が相性が良い

ただし:
- Node サーバをかなり重厚に組みたい
- 既存の Fastify プラグイン資産を厚く使いたい

この 2 条件なら `Fastify` に戻してよい

### 4. ORM は `Prisma` より `Drizzle` を推す

- `Drizzle` 公式 docs は `SQL-like`、`0 dependencies`、`headless` を前面に出している
- 「If you know SQL, you know Drizzle」という思想は、AI にも人間にも都合が良い
- schema、query、migration が TypeScript と SQL の近くにあり、追跡しやすい

判断:
- 実務一点張りで「あとから読めること」を重視するなら、今は `Drizzle` の方が強い
- `Prisma` は依然として有力だが、抽象が 1 層厚い

ただし:
- チーム全体が Prisma に慣れている
- cookbook 的な事例量をより重視したい

この 2 条件なら `Prisma` でも問題ない

### 5. 認証は `Better Auth` がかなり相性良い

- 公式 docs で `framework-agnostic`、`organization & access control`、`plugin ecosystem` を出している
- さらに `AI resources`、`LLMs.txt`、`documentation MCP server`、`Skills` まで用意している

判断:
- 2026 時点で「AI と一緒に進める」前提なら、ここはかなり強い
- ロールや将来の組織対応も見据えやすい

### 6. 非同期ジョブは `BullMQ` が素直

- 公式 docs では Redis ベースの queue、scheduled jobs、retries、parent-child dependencies などが整理されている
- この PJ では Slack 回収、knowledge-vault 回収、AI 分別、通知、連携再試行がある

判断:
- ジョブ基盤は早めに独立前提で置いた方がよい
- ここは今でも `BullMQ` が自然

### 7. フォームは `TanStack Form` より `React Hook Form`

- `TanStack Form` はかなり熱い
- 公式 docs 上でも `new`、`headless form state`、`typed fields`、`granular subscriptions` を強く打ち出している
- ただし、まだ「今から全部これに寄せる」よりは、業務入力の量と複雑さを見て入れる方が安全

- `React Hook Form` は GitHub 上で stars が大きく、`performance`、`UX`、`DX`、`no dependencies`、多くの validation library 対応を打ち出している

判断:
- 初期実装は `React Hook Form`
- 大型で複雑な入力面が増えたら `TanStack Form` を再評価

## 2026-06-23 時点の温度感まとめ

### 本命に置く

- `Next.js`
- `shadcn/ui`
- `Hono`
- `Drizzle ORM`
- `Better Auth`
- `BullMQ`

### かなり熱いが、今回は主軸にしない

- `TanStack Start`
- `TanStack Form`

理由:
- 勢いは強い
- ただし今の PJ は、要件が広く、基盤を早く安定させる必要がある
- そのため「熱い」だけで主軸にせず、1 段控えの候補に置く

### まだ十分有力な代替

- `Fastify`
- `Prisma`

理由:
- 安定、厚い事例、従来の定番としての強みがある
- ただし「AI が扱いやすい explicit さ」では、今回の軸だと少し下がる

## いまの推奨スタック

```text
apps/web         = Next.js + shadcn/ui
apps/admin       = 当初は web 内 route 分離でも可
services/api     = Hono
packages/db      = Drizzle + PostgreSQL
packages/auth    = Better Auth
workers/*        = BullMQ + Redis
forms            = React Hook Form
```

## 次に決めるべきこと

1. `services/api` を Day 1 から `Hono` で分離するか
2. `Drizzle` を採る前提で schema / migration 運用をどう置くか
3. `apps/admin` を最初から別 app にするか
4. `React Hook Form` で始める前提で、どこまで共通 form component を持つか
