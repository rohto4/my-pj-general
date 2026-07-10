# Vikunja結合 受入テスト仕様 2026-07

## 目的

Vikunjaとpj-generalの結合を、画面が開くことだけで完了扱いにしない。
実在する候補、Vikunja task、Webhook、SQLiteまたはPostgreSQLの記録を使って、結合の正しさを確認する。

## テストデータ方針

- pj-generalの既存SQLiteに保存された実在候補を使用する。
- テスト専用のVikunja projectを作成する。
- 候補ID、Vikunja task ID、URL、判断履歴、同期履歴を追跡できる状態にする。
- API token、Webhook secret、Cookieをテスト結果へ出力しない。
- 外部APIのモックだけで本仕様を合格扱いにしない。

## 受入テスト一覧

| ID | 観点 | 操作 | 期待結果 | 証拠 |
| --- | --- | --- | --- | --- |
| VJ-001 | 起動 | Vikunjaとpj-generalを起動する | 両方の画面/APIへ到達できる | health応答、コンテナ状態 |
| VJ-002 | GO登録 | pending候補を1件GOする | 安定版APIでVikunja taskが1件作成される | `decisions`、task ID、task URL |
| VJ-003 | 冪等性 | 同じ候補を再度GOする | 新しいtaskを作らず既存linkを返す | task件数、`execution_links` |
| VJ-004 | 実行状態 | Vikunjaでdone、due date、priorityを変更する | pj-generalの外部実行状態へ反映される | `execution_task_state`、`sync_events` |
| VJ-005 | 署名 | 正しいWebhook署名を送る | eventが処理され200を返す | processing state、HTTP status |
| VJ-006 | 署名不正 | bodyまたは署名を改変する | 401または403で拒否し、候補・実行状態を変更しない | event/error記録、DB差分なし |
| VJ-007 | 重複配送 | 同じ署名付きpayloadを再送する | 二重反映せず成功応答する | dedupe key、処理回数 |
| VJ-008 | API失敗 | Vikunjaを停止してGOする | GO判断を保持し、sync failedとして再試行可能にする | `decisions`、`sync_attempts` |
| VJ-009 | 復旧 | Vikunja再起動後に失敗登録を再試行する | taskを1件だけ作成しsyncedへ遷移する | task件数、attempt履歴 |
| VJ-010 | 中間障害 | 外部task作成後、link保存前の障害を再現する | candidate markerによる再照合で重複を防ぐ | Vikunja検索結果、link復元 |
| VJ-011 | 未知task | linkのないtask eventを送る | raw eventを保持し、候補を変更せず処理済みまたは保留にする | `sync_events` |
| VJ-012 | 外部削除 | Vikunja taskを削除して照合する | candidateとdecisionを残し、linkをdetachedにする | link状態、履歴保持 |
| VJ-013 | 再照合 | Webhookを一時停止してtaskを更新後、照合jobを動かす | API差分から実行状態を修復する | reconcile attempt、state更新 |
| VJ-014 | 再起動 | 両サービスを再起動する | task link、候補、判断、同期状態が残る | 再起動前後DB照合 |
| VJ-015 | バックアップ | DBとVikunja filesを退避・復元する | 対応関係とtask参照が復元される | restore手順、照合結果 |

## 自動化レベル

| レベル | 対象 | 実行場所 |
| --- | --- | --- |
| unit | HMAC検証、API payload生成、状態遷移、冪等キー | pj-general test suite |
| integration | SQLite migration、GO endpoint、Webhook endpoint、再試行記録 | pj-general test server |
| contract | Vikunja安定版APIのmethod/path/response mapping | Linux上の実Vikunja |
| E2E | ブラウザGO、Vikunja画面更新、pj-general反映 | Linux + Windowsブラウザ |
| recovery | 停止、再起動、再照合、backup/restore | Linuxサーバー |

## 合格条件

- VJ-001からVJ-015まで結果と証拠を記録する。
- VJ-002、VJ-003、VJ-004、VJ-005、VJ-006、VJ-008、VJ-009、VJ-014は仮完了前の必須項目とする。
- 未合格項目がある場合は、回避策ではなく未完タスクとして`docs/imp/vikunja-integration-tasks.md`へ戻す。
- plugin / frontend fork / backend forkの必要性は、受入テストと日常操作で観測した不足を根拠に判断する。
