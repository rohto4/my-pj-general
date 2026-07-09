# 技術概念表 2026-07

## 目的

この文書は、`pj-general` の P0 を支える技術選定を、実装前に一枚で把握できるようにするための概念表である。

ここでは処理順や詳細な API ではなく、`どの領域をどの技術が担うか` を固定する。

## 前提

- P0 の入口は `web 手入力`、`Slack`、`Misskey`、`knowledge-vault`
- 入口、AI 分別、業務オブジェクト、権限は自前で握る
- 技術スタック正本は `tech-stack.md`
- Mermaid 図表ルールは `.agents/skills/mermaid-diagram-style/SKILL.md` に置くが、この対応関係は表の方が読みやすいため表形式で管理する

## 技術概念表

| 技術領域 | 採用技術 | 担うこと | 補足 |
| --- | --- | --- | --- |
| 見た目 / 画面 | `Next.js App Router`、`shadcn/ui`、`Tailwind CSS`、`lucide-react` | 入力、確認、一覧、横断ダッシュボード、管理画面 | UI は自前実装。`shadcn/ui` は部品を自分のコードとして持つ前提。 |
| API 境界 | `Hono` | HTTP API、webhook 受付、業務処理への薄い入口 | 重いサーバ FW ではなく、薄く明示的な API 境界を優先する。 |
| DB / 正本 | `PostgreSQL` | 入口イベント、アイデア、タスク、予定、履歴、AI 提案結果の正本 | JSON や全文検索も初期から中期まで PostgreSQL で粘る前提。 |
| DB schema / query | `Drizzle ORM` | schema、migration、型付き query | SQL に近い構造を保ち、後から人間と AI が追いやすくする。 |
| 非同期処理 | `BullMQ`、`Redis` | Slack 回収、Misskey webhook 後処理、knowledge-vault scan、AI 整理、再試行 | 4 入口を P0 に含めるため、Queue は補助ではなく中核寄り。 |
| 認証 / 権限 | `Better Auth` | 自分中心の認証、将来ロール、access control の土台 | 初期は自分専用だが、外部協力者や社内メンバーの仮置きに備える。 |
| 入力 / 検証 | `React Hook Form`、`Zod` | 入力フォーム、確認画面、API payload、config validation | 複雑化したら `TanStack Form` を再評価する。 |
| AI 補助 | `OpenAI API`、必要に応じて `Python` 補助 | 分類、要約、タスク案、予定案、重い変換や解析 | 本体ドメインは TypeScript に寄せ、AI 補助や変換だけ Python を許容する。 |
| 外部入口 | 入口別 integration adapter | `web`、`Slack`、`Misskey`、`knowledge-vault` の取り込み | Misskey は webhook、knowledge-vault は scan、Web は即時登録を基本にする。 |
| 検証 | `Vitest`、`Playwright` | domain / API の unit・integration、ブラウザ E2E | P0 の入力、確認、GO 導線を壊さないために使う。 |

## この図で固定したいこと

- 見た目は `Next.js + shadcn/ui + Tailwind CSS` が担う
- API 境界は `Hono` が担う
- DB 正本は `PostgreSQL` が担う
- DB schema / query は `Drizzle ORM` が担う
- 非同期処理は `BullMQ + Redis` が担う
- 認証と権限の土台は `Better Auth` が担う
- フォームと validation は `React Hook Form + Zod` が担う
- 外部入口は入口別 adapter として扱う

## 設計上の意図

### 1. 入口を増やしても業務モデルを増やさない

`Slack`、`Misskey`、`knowledge-vault`、`web` は入口の違いであり、  
`アイデアカード`、`タスク`、`予定` などの業務 object 自体は共通に保つ。

### 2. P0 から非同期を中心に据える

この PJ は、回収、AI 分別、提案、通知が前提なので、  
Queue を後付けにせず、最初から構造の中心に置く。

### 3. UI と API は近接しつつ分離前提

初速のために `apps/web` で画面を先に作れるようにしつつ、  
業務 API は `services/api` へ逃がせる構造を最初から持つ。

## この次にぶら下げる設計書

- `docs/spec/intake-unified-event-model.md`
- `docs/spec/ai-assisted-registration-flow.md`
- `docs/data/object-model-initial.md`
- `docs/spec/google-calendar-linkage-flow.md`
