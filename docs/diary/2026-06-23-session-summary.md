# 2026-06-23 セッション要約

## 目的

このファイルは、2026-06-23 の検討セッションを `pj-general` 側へ実質引き継ぐための要約である。

このファイルを読めば、今回の会話で何を決め、何を保留し、どこまで docs と knowledge-vault に反映したかを把握できる状態を目指す。

## 今回扱ったテーマ

- やりたいこと抽出フェイズの整理
- PM / ガント / TODO 系 OSS の比較
- 入口自前実装の方針整理
- Codex 運用支援を要件に含める整理
- 実務寄りかつ AI 友好性重視の技術スタック検討
- knowledge-vault との整合確認
- 他 AI にレビュー依頼するためのブリーフ整備

## 今回の主要結論

### 1. プロダクトの中心価値

このプロダクトの中心価値は、`雑な入力を受けて整理し、タスク化・予定化までつなげる入口` にある。

単なるタスク管理ツールではなく、次を一元管理するサイトとして扱う。

- 個人タスク
- チームタスク
- スケジュール
- やりたいこと
- 検討事項
- 気になっている事
- 判断記録
- 知識
- Codex 用プロジェクト開始支援

### 2. UI / 体験の基本方針

- 入口は自前実装
- 4 窓口に分ける
  - 横断ダッシュボード
  - 上位管理者用管理画面
  - 書き入れ口 / 作成口
  - 実績 / 履歴参照
- 入口 UI 基盤候補は `shadcn/ui`

### 3. OSS の役割分担

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
- `Redmine` は本線候補から外した
- `Backlog` は OSS ではない
- `OpenProject` の `Team planner` は Enterprise add-on なので構造参照として扱う

### 4. 技術スタックの現在の推奨

実務性と AI 友好性を重視した現時点の推奨は次の通り。

- Web: `Next.js` App Router
- UI: `shadcn/ui`
- API: `Hono`
- DB: `PostgreSQL`
- ORM / query: `Drizzle ORM`
- Auth: `Better Auth`
- Queue: `BullMQ`
- Queue backend: `Redis`
- Form: `React Hook Form`

補足:
- `TanStack Start` と `TanStack Form` は熱いが主軸採用は保留
- `Fastify` と `Prisma` は代替候補としてまだ有力

### 5. 外部入口の扱い

- Slack を入口にする
- knowledge-vault を入口にする
- 各 1 時間ごとに自分の投稿を回収する
- AI が次へ自動分別する
  - タスク
  - スケジュール
  - 検討事項
  - 気になっている事

### 6. Codex 運用支援も要件に含める

- 初期プロンプト生成
- フォルダ構成ひな型選定
- テンプレート流用元の候補提示
- upstream / 参考 repo の選定補助
- AGENTS.md / PROJECT.md / docs 初期化支援

## 今回追加・更新した主な文書

### `docs/product`

- `idea-to-plan-discovery.md`
- `pm-oss-role-split.md`

### `docs/arch`

- `pm-oss-layered-architecture.md`
- `recommended-oss-and-stack-composition.md`
- `practical-ai-friendly-stack-2026-06.md`

### `docs/candi-ref`

- `oss-candidates-intake-pm.md`
- `oss-candidates-by-visual-priority.md`
- `user-voice-signal-comparison.md`
- `majisemi-article-integration.md`
- `shadcn-and-gantt-constraints.md`
- `adoption-and-recency-reselection.md`
- `demo-comparison-checklist.md`
- `openproject-vs-leantime-integrated-comparison.md`

### `docs/imp`

- `user-tasks.md`
- `user-judge.md`
- `session-discipline.md`
- `next-session-focus.md`
- `ai-review-brief-2026-06-23.md`

### `docs/diary`

- `handoff-2026-06-23-idea-phase.md`
- この `2026-06-23-session-summary.md`

## knowledge-vault 反映状況

今回テーマに関係する直近の `knowledge-vault` 更新は次の 3 件。

- `knowledge/dev/codex-foundation-following-strategy.md`
- `knowledge/dev/self-built-intake-and-layered-pm-oss-selection.md`
- `knowledge/dev/practical-ai-friendly-typescript-stack-2026-06.md`

整合確認済み。

## 今の主要課題

### 1. ドメイン境界

- `アイデアカード` と `タスク` を別 object にするか
- `予定`、`検討事項`、`気になっている事` をどう切るか
- 1 件の入力が複数 object に分かれる時のルールをどうするか

### 2. 正本と同期

- Google Calendar、Slack、knowledge-vault の同期方向
- 重複登録防止
- 冪等性

### 3. AI 分別フロー

- 即確定
- 下書き登録
- 人レビュー必須

このどれを採るか未確定。

### 4. 権限

- 自分
- 外部協力者
- 将来の社内メンバー

この 3 段階を最低限考慮する必要がある。

### 5. Next.js と Hono の責務境界

- `Hono` を Day 1 から分離するか
- 初期だけ `Route Handlers` を併用するか
- 業務ロジックをどこに置くか

## いまの優先論点

次に詰めるべき論点は次の 5 つ。

1. 正本 object を何にするか
2. `Next.js` と `Hono` の責務境界
3. `アイデア -> タスク / 予定 / 検討事項` 昇格ルール
4. AI 分別の確定フロー
5. ロールと可視範囲の最小モデル

## 他 AI にレビュー依頼する準備

他 AI に渡すための単一ファイルは次で作成済み。

- `docs/imp/ai-review-brief-2026-06-23.md`

## 今回の引き継ぎ状態

このセッションの検討内容は、`pj-general` 側 docs と `knowledge-vault` に反映済みであり、次回以降はこのファイル群を正本として継続できる状態である。
