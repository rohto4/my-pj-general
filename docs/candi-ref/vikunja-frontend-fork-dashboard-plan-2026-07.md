# Vikunja frontend fork dashboard計画

作成日: 2026-07-11

## 目的

Vikunjaの実行TODO機能はupstreamを使い続け、標準ビューを毎回切り替えなくても、プロジェクト全体の状態を縦スクロールで確認できる入口をfrontend forkへ追加する。

対象は見た目と読み取り導線であり、Hubの候補・判断データやVikunja backendの中核モデルは変更しない。

## 現状の根拠

- fork clone: `G:\devwork\clone-dir\vikunja-upstream`
- fork origin: `https://github.com/rohto4/vikunja.git`
- upstream remote: `https://github.com/go-vikunja/vikunja.git`
- 基準commit: `e992ed594`
- frontend: Vue 3 + Vite 8 + pnpm 11、Node >= 24
- Vikunja stable image/API: `vikunja/vikunja:2.3.0` / API v1
- 既存のproject viewは `list`、`gantt`、`table`、`kanban`
- Task取得は `TaskCollectionService` の `/projects/{projectId}/views/{viewId}/tasks` を使い、APIページングを持つ
- frontend build成果物はbackendの `frontend/embed.go` に埋め込まれ、既存Dockerfileでcustom imageを作る構成

## 採用する拡張境界

### frontend forkで実装するもの

- `/projects/:projectId/dashboard` ルート
- project名、更新、集計、最近のタスク、今後30日カレンダー、未日付タスクを縦に並べる画面
- 既存のList / Table / Kanban / Ganttへのリンク
- Projectのview切替部分からdashboardへ移動する導線
- Vikunja既存のCSS変数、ボタン、状態色、Taskモデルを使った視覚調和

### 追加しないもの

- Hub専用APIやHub SQLiteへのTask一覧コピー
- Vikunja backendの新規テーブル、認証方式、権限モデル
- Hub候補本文・判断履歴のTasks側保存
- dashboard専用の別Taskモデル
- 既存ビューのドラッグ・編集機能の再実装

## データ取得と期間ルール

1. dashboard初期表示期間は「今日から30日」。月初固定ではなく、開いた日を起点にする。
2. 既存Task APIのページングを利用し、1ページだけで全件と仮定しない。
3. 全件取得が必要な場合はページを順に取得し、loading/error状態を表示する。
4. `startDate` と `endDate` があるtaskは期間バーとして表示する。
5. `startDate` のみなら開始日から `dueDate`、または開始日当日まで表示する。
6. `dueDate` のみなら期限日に表示する。
7. 日付がないtaskはカレンダーから落とさず、未日付一覧に表示する。
8. 30日範囲外でも、期間が重なるtaskは端を切って表示する。
9. 完了taskは状態色を変えるが、初期表示から隠さない。
10. 日付計算はユーザーのVikunja timezoneを前提にし、ブラウザーのUTC変換で日付がずれないようにする。

## 画面構成

```text
project header
  dashboard / 既存ビュー / 更新
summary metrics
  全件 / 未完了 / 完了 / 期限超過 / 今後30日
priority and recent tasks
  タスク名 / 状態 / 優先度 / 期限 / 担当 / 進捗
30-day calendar
  日付列 / task bar / 期限マーカー
undated tasks
  日付なしtaskの一覧
existing views
  List / Table / Kanban / Ganttへの操作リンク
```

「各タブを1枚に複製する」のではなく、日常確認に必要な情報をdashboardへまとめ、編集・並べ替えなどの本来の操作は既存viewへ戻す。これによりfork差分を小さく保ち、upstream追随時の競合箇所をroute、wrapper、dashboard componentに閉じ込める。

## Hub / Intakeとの連結

- Hubの `Tasks側を開く` は `/projects/{projectId}/dashboard` へ向けられる候補とする。既存の標準project URLはfallbackとして残す。
- 確認待ち詳細のtask URLは個別task `/tasks/{taskId}` のままにする。
- HubのGO処理は既存の `POST /api/candidates/:id/execution` を使い、dashboard追加のために変更しない。
- HubはVikunja task一覧を保持せず、概要APIの読取結果だけを表示する。
- Tasks側からHubへ戻す導線は、候補本文を同期するためではなく、Hubの確認・履歴へ戻るための明示リンクが必要になった場合に追加する。

## build・配信

1. fork専用branchを作る。
2. frontend component、router、wrapper、unit testを先に変更する。
3. `pnpm typecheck`、`pnpm lint`、`pnpm test:unit`、`pnpm build` を通す。
4. Dockerfileでfrontend distをbackendへembedしたcustom imageを作る。
5. Linux上でcustom imageを別tagで起動し、既存Vikunja DBとenvを変更せずに動作確認する。
6. Hubの公開URL、Vikunjaの公開URL、API token、Webhook secretをcustom imageへ埋め込まない。
7. rollbackは現在のstable image tagへ戻すだけでdashboard差分を切り離せるようにする。

## upstream追随リスク

| リスク | 対策 |
| --- | --- |
| routerやProjectWrapperのupstream変更 | fork差分をdashboard routeと導線追加に限定し、upstream merge後にtypecheckを必須化 |
| Task APIのページング・フィールド変更 | `TaskCollectionService` と `ITask` を使い、独自fetcherを増やさない |
| CSS変数や共通部品変更 | Vikunja既存の変数・BaseButton・Iconを使い、dashboard専用の大規模テーマを作らない |
| frontend distのembed失敗 | custom image buildを受入条件に含め、公式imageを直接置換しない |
| task件数増加による遅延 | 全件取得の上限・ページング・表示件数を決め、最初は最近タスクと期間taskを優先する |
| AGPLv3運用 | forkのsource、LICENSE、変更履歴、custom imageの公開方針を残す |

## 判断待ちではないが、試作後に確認する点

- Hubの主リンクを標準project URLからdashboard URLへ切り替えるか。
- dashboardの30日カレンダーに、期間外のtaskも表示するか。
- 既存viewの概要をdashboard内にどこまで再現し、どこからリンク遷移にするか。
- タスク追加・完了変更をdashboard内で許可するか。初版は既存Task画面へ委譲する。

## 関連正本

- `docs/imp/current-goal-and-data-structure-brief-2026-07-11.md`
- `docs/imp/p0-status-audit-2026-07-11.md`
- `docs/data/vikunja-integration-data-design-2026-07.md`
- `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
- `docs/imp/vikunja-integration-tasks.md`
