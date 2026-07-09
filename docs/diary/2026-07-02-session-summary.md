# 2026-07-02 セッション要約

## 目的

このファイルは、2026-07-02 のセッション内容を次回へ引き継ぐための要約である。

このセッションでは、P0 設計書の作成、Mermaid 図の整理、knowledge-vault 記載方針の中央化、ユーザー判断待ちと Codex 実装待ちの分離を進めた。

## 今回の主要成果

### 1. knowledge-vault 記載方針の中央化

- `G:\knowledge-vault\knowledge-vault-write-policy.md` を中央正本として作成した。
- `pj-general` 側には policy 本文を置かず、`AGENTS.md` から中央 policy を読む運用に変更した。
- `G:\knowledge-vault\memory\l1-triggers.md` に policy への想起入口を追加した。
- `memory/` の L1〜L4 階層について、中央 policy に補足した。

### 2. Mermaid 図作成ルールの整備

- `.agents/skills/mermaid-diagram-style/` を作成した。
- 技術概念図は図より表の方が適切と判断し、`docs/arch/technical-concept-diagram-2026-07.md` を技術概念表として整理した。
- フロー図では、ユーザー操作点と自動処理点を見た目で区別する方針にした。
  - `ユーザー` actor ノードを追加する。
  - ユーザー操作点へ actor から矢印を出す。
  - 自動処理は紫系ノードと `自動処理` ラベルで示す。

### 3. P0 設計書の作成

今回作成または更新した主な P0 設計書は次。

- `docs/product/p0-overall-workflow-2026-07.md`
- `docs/data/p0-data-flow-2026-07.md`
- `docs/spec/intake-unified-event-model.md`
- `docs/spec/ai-assisted-registration-flow.md`
- `docs/data/object-model-initial.md`
- `docs/spec/google-calendar-linkage-flow.md`
- `docs/spec/codex-project-bootstrap-flow.md`

P0 の主要縦線は、次のようにつながる状態になった。

```text
4入口
  -> Raw入口イベント
  -> 正規化イベント
  -> AI整理結果
  -> ユーザーGO
  -> 業務object
  -> 予定化 / Codex開始支援
```

### 4. 技術スタック整理

- `tech-stack.md` を現時点の技術スタック正本として更新した。
- `docs/arch/tech-stack-decision-matrix-2026-07.md` を作成した。
- 現時点の推奨は次。
  - Next.js App Router
  - shadcn/ui
  - Hono
  - PostgreSQL
  - Drizzle ORM
  - Better Auth
  - BullMQ
  - Redis
  - React Hook Form
  - Zod

## 今回の判断済み事項

`docs/imp/user-judge.md` に反映済み。

- Google Calendar 連携は、ユーザー GO で登録できるところまでを P0 対象にする。
- 外部協力者に最初から見せる情報は、スケジュールを中心にする。
- MVP にガントチャートは入れる。
- MVP にキャパ管理は入れない。
- Codex プロジェクト起動支援は、スケジュールページではなく、作業者用 / タスクサマリページをトリガーページにする。
- 4 つの窓口ごとの表示内容と操作範囲は定義済みとして扱う。

## 現在のユーザー判断待ち

`docs/imp/user-judge.md` と `docs/imp/user-tasks.md` を正本にする。

- `UJ-01`: Slack / knowledge-vault から回収する対象範囲をどこまでにするか。
- `UJ-02`: 回収後の AI 自動分別をどこまで自動確定させるか。
- `UJ-03`: 自動確定しない場合、確認待ちキューで何を表示して GO させるか。

## Codex が次に進められるタスク

`docs/imp/imp-tasks.md` と `docs/imp/next-session-focus.md` を正本にする。

ユーザー判断を待たずに進められるもの。

1. `docs/spec/screen-structure-p0.md` を作る。
2. `docs/spec/gantt-mvp-flow.md` を作る。
3. `docs/spec/classification-tag-master.md` を作る。
4. `docs/spec/role-and-permission-initial.md` を作る。
5. `docs/spec/prompt-template-management.md` を作る。
6. `docs/spec/intake-source-adapters.md` を下書きする。
7. 設計書内に混ざった進行管理記述を `docs/imp/` 系へ分離する。

ユーザー判断後に進めるもの。

- `UJ-01` 後: Slack / knowledge-vault 回収対象範囲を反映した `intake-source-adapters` の確定版を作る。
- `UJ-02` 後: AI 自動分別をどこまで自動確定させるかを `ai-assisted-registration-flow` に反映する。
- `UJ-03` 後: 確認待ちキューの表示項目と GO 操作を画面仕様へ反映する。

## 現在のブロッカー

- アプリ実装開始を止めるブロッカーはまだない。
- Slack / knowledge-vault adapter の確定版は `UJ-01` 待ち。
- AI 自動確定の詳細仕様は `UJ-02` 待ち。
- 確認待ちキューの詳細仕様は `UJ-03` 待ち。

## 重要な注意点

- `docs/spec/*`、`docs/product/*`、`docs/data/*` には、要件・設計判断を残す。
- 実装待ち、判断待ち、次アクションは `docs/imp/` 系へ分離する。
- `knowledge-vault` へ書く前には `G:\knowledge-vault\knowledge-vault-write-policy.md` を読む。
- `knowledge-vault` へは、PJ 固有の進行ではなく横断価値のある知見だけを残す。

## 次回最初に読むとよいファイル

1. `AGENTS.md`
2. `PROJECT.md`
3. `tech-stack.md`
4. `docs/imp/user-tasks.md`
5. `docs/imp/user-judge.md`
6. `docs/imp/imp-tasks.md`
7. `docs/imp/next-session-focus.md`
8. `docs/product/p0-overall-workflow-2026-07.md`
9. `docs/data/p0-data-flow-2026-07.md`
10. `docs/spec/intake-unified-event-model.md`
11. `docs/spec/ai-assisted-registration-flow.md`
12. `docs/data/object-model-initial.md`
13. `docs/spec/google-calendar-linkage-flow.md`
14. `docs/spec/codex-project-bootstrap-flow.md`

## 現時点の引き継ぎ状態

P0 設計は、入口、AI 整理、業務 object、Google Calendar 連携、Codex 開始支援まで一通り接続済み。

次は、画面構成、ガント MVP、タグマスタ、初期権限、プロンプトテンプレート、入口 adapter の設計へ進める状態である。
