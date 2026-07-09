# Tech Stack

## 位置づけ

この文書は `pj-general` の技術スタック正本である。

現時点では要件定義前フェーズのため、ここに書く内容は「実装確定」ではなく「次に土台を作るときの第一候補」として扱う。
古い検討文書に残っている `Fastify + Prisma` 方針より、2026-06 時点の再評価では `Hono + Drizzle` を優先候補に置く。

比較経緯と候補群の整理は `docs/arch/tech-stack-decision-matrix-2026-07.md` を参照する。

## プロダクト方針

- 入口、AI 分別、業務オブジェクト、権限は自前で握る
- ガント、TODO、横断計画、スケジュール表示は OSS の思想や一部実装を参照する
- OSS は丸ごと採用ではなく、レイヤーごとに借りる
- 入口 UI は自前実装し、`Plane` と `Leantime` の体験を参考にする
- 横断計画やガントは `OpenProject` を主参照にする

## 採用第一候補

| 領域 | 第一候補 | 用途 |
| --- | --- | --- |
| Runtime | Node.js LTS | TypeScript 実行基盤 |
| Package manager | pnpm | workspace / monorepo 管理 |
| Monorepo | Turborepo | apps / services / packages / workers のタスク実行 |
| Web | Next.js App Router | `apps/web` の画面と BFF 近接処理 |
| UI | shadcn/ui | 自前で編集できる UI 部品 |
| Style | Tailwind CSS | UI スタイリング |
| Icon | lucide-react | 操作ボタン、状態表示、ツールアイコン |
| API | Hono | `services/api` の薄い HTTP API |
| DB | PostgreSQL | 中核データの正本 |
| ORM / Query | Drizzle ORM | SQL に近い TypeScript schema / query |
| Auth | Better Auth | 認証、組織、アクセス制御の土台 |
| Queue | BullMQ | 定期回収、AI 分別、通知、再試行 |
| Queue backend | Redis | BullMQ backend / cache |
| Form | React Hook Form | 入力フォーム |
| Validation | Zod | API / form / config の schema validation |
| Test | Vitest | unit / integration test |
| E2E | Playwright | ブラウザ動作確認 |
| Lint / Format | ESLint / Prettier | 品質と整形 |

## 代替候補

| 領域 | 代替 | 採る条件 |
| --- | --- | --- |
| Web | TanStack Start | RC 状態が解け、要件に合う強い理由が出た場合 |
| API | Fastify | Node サーバを重厚に組み、既存 plugin 資産を厚く使う場合 |
| ORM | Prisma ORM | チームの慣れ、事例量、管理画面系生成を重視する場合 |
| Form | TanStack Form | 複雑な型付きフォームが増え、React Hook Form でつらくなった場合 |

## モノレポ配置

```text
apps/
  web/              # Next.js。書き入れ口、横断ダッシュボード、履歴参照
  admin/            # 将来分離候補。初期は apps/web の route group でも可
services/
  api/              # Hono。業務 API、認可評価、外部連携 API
packages/
  domain/           # アイデア、タスク、予定、ロールなどの純粋ドメイン
  db/               # Drizzle schema / migrations / query helpers
  auth/             # Better Auth 設定と権限補助
  ui/               # shadcn/ui ベースの共通 UI
  integrations/     # Slack、Google Calendar、knowledge-vault 連携
workers/
  sync/             # Slack / knowledge-vault 定期回収
  ai/               # AI 分別、要約、タスク案生成
  notify/           # 通知、再試行、リマインド
infra/
  local/            # docker compose などローカル基盤
tests/
  e2e/              # Playwright
```

## 初期導入の順番

1. `pnpm-workspace.yaml` と root `package.json` を作る
2. `turbo`、`typescript`、`eslint`、`prettier` を入れる
3. `apps/web` を `Next.js + Tailwind CSS` で作る
4. `shadcn/ui` と `lucide-react` を入れる
5. `packages/domain` と `packages/db` の空パッケージを作る
6. `services/api` を `Hono` で作る
7. `PostgreSQL + Redis` のローカル compose を用意する
8. `Drizzle`、`Better Auth`、`BullMQ` を接続順に入れる
9. `Vitest` と `Playwright` を最低限入れる

## PowerShell リファレンス

この PJ の標準シェルは当面 PowerShell とする。

### 基本方針

- ファイル読み書きは UTF-8 を明示する
- ファイル探索は `rg` / `rg --files` を優先する
- 削除や移動は `Remove-Item` / `Move-Item` に `-LiteralPath` を使う
- `cmd /c` と PowerShell の混在で破壊的操作をつながない
- secret、token、cookie、未公開認証情報を出力しない

### よく使う確認コマンド

```powershell
Get-Content -LiteralPath AGENTS.md -Encoding UTF8
Get-ChildItem -LiteralPath docs -Recurse -File
rg --files docs
rg "検索語" docs
git status --short --branch
git remote -v
```

### npm / pnpm 実行

```powershell
node --version
npm --version
corepack enable
pnpm --version
pnpm install
pnpm dev
pnpm test
pnpm lint
```

## Python リファレンス

Python はアプリ本体の主言語ではなく、調査、変換、検証、ドキュメント処理の補助に使う。

### 主な用途

- CSV / JSON / Markdown の変換
- OSS 比較データの整形
- PDF / docx / spreadsheet の検証補助
- 一時的な集計や可視化
- 大量テキストの正規化

### 基本方針

- アプリ本体の業務ロジックを Python に分散させない
- 使い捨てスクリプトは `tmp/`、継続利用するものは `scripts/` に置く
- 入出力は UTF-8 を明示する
- secret をコードや引数に直書きしない

### よく使う確認コマンド

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python scripts/example.py
```

## Git / GitHub リファレンス

### 現在の remote

```text
origin = https://github.com/rohto4/my-pj-general.git
```

### 基本方針

- 作業前後に `git status --short --branch` を見る
- ユーザー由来の未コミット変更は勝手に戻さない
- secret を commit しない
- 大きな設計変更は docs に判断理由を残す

### よく使うコマンド

```powershell
git status --short --branch
git diff --stat
git diff
git add <path>
git commit -m "message"
git push origin main
```

## ローカル基盤

初期のローカル依存は次を想定する。

- Node.js LTS
- pnpm
- Docker Desktop
- PostgreSQL
- Redis
- Git Credential Manager
- PowerShell
- Python 3

`Docker Desktop` は PostgreSQL / Redis をローカルに直接入れず、compose で揃えるために使う。

## 外部連携候補

| 対象 | 用途 | 初期方針 |
| --- | --- | --- |
| Google Calendar | タスクの予定化、予定確認 | 初期は登録導線か直接登録か未決 |
| Slack | 自分の投稿回収、タスク候補抽出 | 1 時間ごとの回収候補 |
| knowledge-vault | 知識、検討事項、気になる事の回収 | 既存 vault を入口として扱う |
| OpenAI API | AI 分別、要約、タスク案生成 | secret は repo に置かない |

## 未決事項

- `services/api` を Day 1 から `Hono` で分離するか
- `apps/admin` を最初から別 app にするか
- Google Calendar 連携を初期版で直接登録まで行うか
- Slack / knowledge-vault の AI 分別を即確定にするか、確認キューを挟むか
- ガントを表示だけ借りるか、編集体験まで借りるか

## 参照元

- `docs/arch/practical-ai-friendly-stack-2026-06.md`
- `docs/arch/recommended-oss-and-stack-composition.md`
- `docs/arch/pm-oss-layered-architecture.md`
- `docs/arch/tech-stack-decision-matrix-2026-07.md`
- `docs/product/idea-to-plan-discovery.md`
