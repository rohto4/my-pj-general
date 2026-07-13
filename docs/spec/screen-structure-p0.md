# P0 画面構成仕様

作成日: 2026-07-09

## 目的

P0 でユーザーが触る画面構成を定義する。

初期版は `apps/web` の静的プロトタイプとして始めたが、2026-07-10 時点では SQLite 永続化と最小 API を持つ本デモ状態へ移行している。認証、本 AI、Google Calendar 登録、Misskey 実接続はまだ対象外だが、Web 手入力、knowledge-vault import、Slack import payload、確認待ち操作、ダッシュボード集計、ガント表示は同じ SQLite データを使う。

## P0 薄く実装 1 版の画面

| 画面 | 目的 | 初期実装 | 参照 |
| --- | --- | --- | --- |
| 横断ダッシュボード | 確認待ち、GO済み、予定候補、取り込み元、判断ログを俯瞰する | 左サマリ列、処理フロー、優先確認、判断ログ | OpenProject、shadcn/ui Blocks |
| TODO / タスク管理へ遷移 | GO済みタスクを日常的に実行・更新する | Vikunja TODO を主遷移先にし、接続状態と概要を表示する | Vikunja Tasks |
| ガント補助表示 | TODO / ScheduleCandidate の期間、担当、進捗、依存を必要時だけ読む | P0 の read-only weekly timeline は補助表示。外部ガント専用遷移は作らない | Vikunja Gantt |
| 確認待ちキュー | AI 整理結果を人が GO / 編集 / 不要 / アーカイブに分ける | table、filter、detail pane、actions | shadcn/ui Tasks、Plane Intake |
| 作業者用 / タスクサマリ | 今日見るタスクと Codex 起動支援を確認する | today focus、Codex prompt preview | Linear、Plane |
| 管理画面の最小範囲 | P0 の入口、タグ、ロール、AI確定方針、プロンプトテンプレート、取り込み対象を確認する | DB由来の source settings、tag master、prompt template、import action | NocoBase、OpenProject |

書き入れ口 / 作成口は画面順序の section ではなく、右側から出る drawer として常時呼び出せる形にする。

## 初期 navigation

```text
横断
TODO
確認待ち
作業者
管理
```

1 つの `apps/web` 内で section navigation として実装する。P0 では route 分割は必須にしない。

## 確認待ちキューの操作

| 操作 | P0 動作 |
| --- | --- |
| `GO` | candidate を `approved` にする |
| `編集` | candidate を `edited` にする |
| `不要` | candidate を `rejected` にする |
| `アーカイブ` | candidate を `archived` にする |

P0 本デモ状態では、操作状態は SQLite の `candidates.status` と `decisions` に保存する。GO 後の業務 object 作成はまだ薄く、preview と decision log を優先する。

## P0 デモに含める入口

| 入口 | P0 data |
| --- | --- |
| Web | drawer の manual intake を SQLite へ保存 |
| Slack | `memo-ideas` / `C0BG4TCPAUD`。connector / 手動 import payload を `/api/import/slack` へ渡す |
| Misskey | P0未接続。候補件数0の無効sourceとして表示 |
| knowledge-vault | `inbox`, `records`, `tasks`, `memory` を `/api/import/knowledge-vault` で `KV-*` 候補化 |

## P0 では作らないこと

- 本認証。
- 外部 DB サーバ。
- アプリ単体での Slack API 認証保持。
- Misskey webhook 接続。
- Misskey 実接続。
- Google Calendar API 登録。
- AI 実行。
- 自動確定。

## 実装対応

- `apps/web/index.html`
- `apps/web/styles.css`
- `apps/web/app.js`
- `apps/web/server.mjs`
- `apps/web/db_tool.py`
- `apps/web/data/p0.sqlite`（ローカル生成、git 管理外）
