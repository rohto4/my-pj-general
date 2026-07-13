# 現在のゴールと実装予定データ構造

> 2026-07-12に役割を終了した履歴ブリーフ。現行のP0判定は `docs/imp/p0-completion-audit-2026-07-12.md`、P1は `docs/product/p1-phase-brief-2026-07.md` を正本とする。

作成日: 2026-07-11
用途: 別セッションで Hub / Tasks 側の見た目を検討するための引継ぎ用ブリーフ

> この文書は短い引継ぎ資料であり、確定仕様の正本ではない。データの正本は `docs/data/vikunja-integration-data-design-2026-07.md`、責務境界の正本は `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md` とする。

## 1. 現在の最優先ゴール

最終的には、次の3つを一続きの実データ導線として確認できる状態にする。

```text
入口
  Web / Slack memo-ideas / knowledge-vault
    -> Hub
       原文・出典・AI候補・不足項目・確認待ち・判断履歴
         -> ユーザーが GO
            -> Tasks
               Vikunja の実行 TODO、期限、担当、進捗、完了
```

### 現在の作業順

1. Hub の P0 実装、SQLite 永続化、入口、確認待ち、管理画面、GO導線の不足を洗い出す。
2. Hub と Vikunja のデータ連結・導線連結を実データで維持する。
3. Vikunja は upstream backend をできるだけ維持し、frontend fork で見づらい標準画面を補う。
4. Vikunja 側に、既存のタスク一覧・テーブル・カンバン・ガントへ到達できるスクロール式ダッシュボードを追加する。
5. ダッシュボードの初期表示は「今日から今後30日」の固定期間カレンダーとし、日付のないタスクは別の未日付一覧に出す。
6. データ導線が崩れていないことを確認した後、Hub と Tasks のブルー + シルバー + ソリッド基調をさらに調和させる。

## 2. P0の現在状態

### 実装済みとして扱う範囲

- Hub の横断ダッシュボード、入口別量、候補種類、処理フロー、優先確認、判断ログ。
- Web書き入れ口と SQLite 永続化。
- knowledge-vault の `inbox`、`records`、`tasks`、`memory` の取り込み対象。
- Slack `memo-ideas` の connector payload / 手動 payload import 経路。
- 確認待ちの `GO`、`編集`、`不要`、`アーカイブ` と判断履歴。
- 管理画面の入口、タグ、ロール、AI方針、プロンプト、取り込み対象の最小設定。
- Hub から Vikunja の project 概要・直近タスクを読む API。
- Hub の GO から Vikunja task を作り、外部ID・URL・状態を保持する連結。
- Vikunja Webhook / 再照合による実行状態の状態ミラー。
- Linux上の Hub + Vikunja 実機起動と、実taskの作成・状態反映確認。

### この作業で残っている確認・拡張

- P0画面をユーザーが触った最終受入と、必要なUI微調整。
- Vikunja frontend fork のブランチ、dashboard route、既存Task API利用、ビルド・配信方法。
- 今後30日カレンダーの表示細部、日付なしタスク、期限だけのタスク、期間タスクの扱い。
- Hubの表示をどこまでTasks側へ寄せるか。

### P0の範囲外として後段に分離

- Misskeyの実接続。
- AIによる自動分類・部分自動GO。
- 認証・複数ユーザー・権限の本実装。
- 6時間ごとのLinux定期入口回収 worker。
- PostgreSQL、Redis / BullMQへの常設移行。
- HubとTasks間の候補本文・判断の双方向同期。

## 3. システム責務とデータ所有権

| 領域 | 正本 | 役割 |
| --- | --- | --- |
| Hub / pj-general | SQLite（将来 PostgreSQL） | 入口原文、出典、AI候補、不足項目、ユーザー判断、同期履歴 |
| Tasks / Vikunja | VikunjaのDB | GO後の実行TODO、期限、担当、進捗、完了、Tasks側の画面状態 |
| HubのTasks概要 | Vikunja APIの読取結果 | project概要・直近タスクを表示する一時的なProjection。Hubにタスク一覧の別正本を作らない |
| Hubの状態ミラー | Hub SQLite | 候補と外部taskの対応、done・期限・担当・進捗など、確認表示に必要な最小状態 |

重要な境界:

- GO前の候補と判断はHubにある。Vikunjaには送らない。
- GO時にHubからVikunjaへtaskを作成する。
- GO後の実行内容はVikunja側で完結する。
- Webhook / 再照合で戻すのは実行状態だけ。候補本文や判断履歴は書き換えない。
- Vikunja frontend dashboardは、既存VikunjaのTask APIを読むUI拡張であり、Hub SQLiteに新たなTask正本を追加しない。

## 4. Hub SQLiteの現行スキーマ

現行の実装は `apps/web/db_tool.py` が起動時にSQLite schemaを作る。DBファイルの既定場所は `apps/web/data/p0.sqlite` で、`P0_DB_PATH` で差し替えられる。

### 入口・候補・判断

```text
sources
  id, label, path, enabled, source_kind, last_imported_at

candidates
  id, status, title, kind,
  source_id, source_label, source_path,
  confidence, missing_json, occurred,
  excerpt, summary, todo, schedule, preview,
  created_at, updated_at

tags
  id, name, category, color, visible

candidate_tags
  candidate_id, tag_id

decisions
  id, candidate_id, action, note, created_at
```

候補の主な状態は、少なくとも `pending`、`edited`、`approved`、`rejected`、`archived` を扱う。判断履歴は候補の現在状態と分けて `decisions` に積む。

### 管理・表示補助

```text
settings
  key, value_json

prompt_templates
  id, name, target, body, enabled

gantt_tasks
  id, title, owner, progress, start, span, state, dependency
```

`gantt_tasks` legacy tableはschema互換のため残るが、画面データには使わない。現行表示は日付付きcandidateと `execution_task_state` から生成する。

### Vikunjaとの対応・同期

```text
execution_links
  candidate_id PK,
  provider, external_project_id, external_task_id,
  external_url, sync_state, last_synced_at,
  created_at, updated_at

execution_task_state
  candidate_id PK,
  title, done, due_date, priority,
  assignees_json, percent_done,
  external_updated_at, mirrored_at

sync_events
  id, dedupe_key UNIQUE, external_event_id,
  provider, event_type, payload_hash, payload_json,
  received_at, processed_at, processing_state, error

sync_attempts
  id, candidate_id, provider, direction, operation,
  idempotency_key UNIQUE, state, error, attempted_at
```

冪等性の基本は `provider + candidate_id` で同じ候補を二重登録しないこと。Webhookの重複排除は外部event ID、なければpayload hashを材料にした `dedupe_key` を使う。

## 5. HubからTasksへ渡るデータ

GO時にVikunja taskへ送る最小内容は次の通り。

```json
{
  "title": "候補タイトル",
  "description": "候補要約\n\nTODO案\n\ncandidate: AI-001"
}
```

Hub側には作成後、次の対応を保存する。

```json
{
  "candidateId": "AI-001",
  "provider": "vikunja",
  "externalProjectId": "1",
  "externalTaskId": "123",
  "externalUrl": "http://<vikunja>/tasks/123",
  "syncState": "synced"
}
```

現在の実装では、期限・担当・進捗の入力をHubからTasksへ完全に移送する設計ではない。登録後はVikunja側で編集し、Webhook / 再照合で状態をHubへ反映する。

## 6. Vikunja dashboardで読むデータ

frontend forkのdashboardは、Vikunja既存のproject task APIを使う。新しいHub専用APIやVikunja専用テーブルは最初から追加しない。

画面で必要なTask表示項目:

```text
id
title
done
priority
percentDone / percent_done
startDate / start_date
dueDate / due_date
endDate / end_date
assignees[].username または name
updated / updatedAt
projectId
```

表示構成の初版:

1. project見出しと更新。
2. 全件数、未完了、完了、期限超過、今後30日件数の集計。
3. タスク一覧または最近のタスク。
4. 今日から30日を横に並べる固定期間カレンダー。
5. 期間があるタスクは開始日から終了日、終了日がなければ期限までを配置。
6. 期限だけのタスクはその日に配置。
7. 日付がないタスクは「未日付タスク」へ分離。
8. 既存のList / Table / Kanban / Gantt viewへの導線を残す。

カレンダーは「今月」ではなく、初期値を「今日から30日」とする。実装時に前後移動や日付指定を追加する場合も、デフォルトの表示期間はこのルールを崩さない。

## 7. 別セッションでモックを作るときの表示優先順位

### Hub側

- 入口別の量
- 候補の種類
- 優先確認
- 処理フロー
- 確認待ち候補の詳細
- GO済み候補とTasks側URL
- Vikunja projectの全件数 / 未完了 / 完了 / 最近のtask

### Tasks側

- project名
- タスク名、完了状態、優先度
- 期限・開始日・終了日
- 担当者
- 進捗
- 今後30日カレンダー
- 未日付タスク
- 既存Vikunja viewへのリンク

### 表示してはいけない誤解

- HubがVikunjaのTask一覧をSQLiteに複製して所有しているように見せない。
- GO前のAI候補がVikunja側に登録済みのように見せない。
- VikunjaからHubへ候補本文・判断が逆流するように見せない。
- P0で未実装のMisskey実接続、AI自動GO、定期workerを実装済みのように見せない。

## 8. 実装時の検証ポイント

- HubのGOで実Vikunja taskが1件作成される。
- 同じ候補を再GOしても二重作成されない。
- HubからTasksのproject / task URLへ遷移できる。
- Vikunja側で完了・期限・進捗を変更すると、Hubの状態表示だけが更新される。
- Tasks dashboardは日付なしtaskを落とさない。
- 30日範囲にtaskが0件でも、空のカレンダーと未日付一覧を表示できる。
- 既存VikunjaのList / Table / Kanban / Ganttの操作導線を壊さない。
- Hub側のSQLiteデータ、Vikunja側のDB、API tokenを画面やログに露出しない。

## 関連正本

- `docs/imp/imp-tasks.md`
- `docs/imp/p0-production-demo-tasks.md`
- `docs/data/vikunja-integration-data-design-2026-07.md`
- `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
- `docs/imp/vikunja-integration-tasks.md`
- `apps/web/db_tool.py`
- `apps/web/server.mjs`
- Vikunja fork: `G:\devwork\clone-dir\vikunja-upstream`
