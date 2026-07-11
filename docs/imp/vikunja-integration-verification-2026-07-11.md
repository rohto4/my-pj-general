# Vikunja実機結合 検証結果 2026-07-11

## 対象

- Vikunja: `v2.3.0`
- project: `1 / Inbox`
- pj-general: Linux Docker container、Node 24 + Python + SQLite
- 候補: `KV-e378384856 / L1 Triggers`
- Vikunja task: `#1 / L1 Triggers`

private IP、API token、Webhook secretはリポジトリへ記録しない。

## 受入結果

| ID | 結果 | 証拠・現在地 |
| --- | --- | --- |
| VJ-001 | 合格 | Vikunja `:3456`、pj-general `:4173`、両コンテナとAPIへ到達 |
| VJ-002 | 合格 | 実候補GOからVikunja task `#1`を作成 |
| VJ-003 | 合格 | 再GO後もtask IDとlink件数が1 |
| VJ-004 | 保留 | Vikunja完了操作は成功。Webhook配送がprivate IP拒否で未反映 |
| VJ-005 | 部分合格 | HMAC受信はintegration test合格。実配送はVJ-004と同じゲート |
| VJ-006 | 自動合格 | 不正署名401をserver実装とintegration testで確認 |
| VJ-007 | 自動合格 | 同一payloadを2回送信し`sync_events`が1件 |
| VJ-008 | 合格 | network timeout時もapproved判断とfailed attemptを保持 |
| VJ-009 | 合格 | network修正後の再試行でtaskを1件だけ作成 |
| VJ-010 | 未実施 | task作成後・link保存前の障害注入が必要 |
| VJ-011 | 自動合格 | link不明eventをorphanとして保持する実装あり |
| VJ-012 | 未実施 | 外部削除とdetached反映が未実装 |
| VJ-013 | 未実施 | 定期reconcile workerが未実装 |
| VJ-014 | 部分合格 | コンテナ再作成後もSQLite候補・linkを保持。Webhook反映後に再確認 |
| VJ-015 | 未実施 | backup/restore実証が必要 |

## 実測した設計差分

1. Docker内からLAN公開IPへのhairpin接続がtimeoutしたため、内部API URLと公開リンクURLを分離した。
2. VikunjaのWebhook配送はprivate Docker IPをSSRF保護で拒否した。専用networkだけを使う構成でも明示設定が必要だった。
3. ホストへNodeを導入せず、pj-generalをPython同梱コンテナにした。
4. `latest`コンテナの実versionは2.3.0だったが、再pullによるdrift防止のためComposeを2.3.0へ固定する必要がある。

## 次の1手

ユーザー承認後、Vikunjaへ`VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS=true`を設定し、imageを`2.3.0`へ固定して再起動する。その後task `#1`を未完了・完了へ切り替え、VJ-004 / VJ-005 / VJ-014を再検証する。
