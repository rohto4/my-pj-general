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
| VJ-004 | 合格 | 実taskの完了、priority 3、期限、担当`unibell`をpj-generalへ反映 |
| VJ-005 | 合格 | 実署名Webhook 2件を受信し、いずれも`task.updated / processed` |
| VJ-006 | 自動合格 | 不正署名401をserver実装とintegration testで確認 |
| VJ-007 | 自動合格 | 同一payloadを2回送信し`sync_events`が1件 |
| VJ-008 | 合格 | network timeout時もapproved判断とfailed attemptを保持 |
| VJ-009 | 合格 | network修正後の再試行でtaskを1件だけ作成 |
| VJ-010 | 未実施 | task作成後・link保存前の障害注入が必要 |
| VJ-011 | 自動合格 | link不明eventをorphanとして保持する実装あり |
| VJ-012 | 自動合格 | 実Vikunja 404を`detached`へ反映するintegration testに合格。実task削除は未実施 |
| VJ-013 | 合格 | 実task `#1`のdone状態を再照合APIからSQLiteへ修復 |
| VJ-014 | 合格 | 両コンテナ再起動後も候補19件、link 1件、done状態を保持 |
| VJ-015 | 合格 | 両SQLiteをonline backupし、別DBへのrestoreと`integrity_check=ok`を確認 |

## 実測した設計差分

1. Docker内からLAN公開IPへのhairpin接続がtimeoutしたため、内部API URLと公開リンクURLを分離した。
2. VikunjaのWebhook配送はprivate Docker IPをSSRF保護で拒否した。専用networkだけを使う構成でも明示設定が必要だった。
3. ホストへNodeを導入せず、pj-generalをPython同梱コンテナにした。
4. `latest`コンテナの実versionは2.3.0だったため、再pullによるdrift防止としてComposeを`2.3.0`へ固定した。
5. Webhook配送が停止しても、`POST /api/integrations/vikunja/reconcile`で実行状態を修復できた。

## 次の1手

主要な実機結合項目とHubのTasks概要・導線・2段階UI洗練は完了した。次はユーザーの微調整を受ける。

## 実Webhook証拠

- Vikunja setting: `VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS=true`
- image: `vikunja/vikunja:2.3.0`
- 未完了反映: pj-general `done=0`、event `task.updated / processed`
- 完了反映: pj-general `done=1`、event累計2件、両方`processed`
- link state: `synced`
- 属性反映: `priority=3`、`due_date=2026-07-20T12:00:00Z`、assignee `unibell`
- task description: 出典、TODO、`candidate: KV-e378384856`を保持

## API更新契約の実測差分

- `POST /api/v1/tasks/{task}`へpriorityとdue dateだけを送ると、省略した`done`と`description`がzero valueへ戻った。
- task更新はPATCHとして扱わず、GETした現在値からmutable fieldを保持するread-modify-writeが必要。
- `GET /api/v1/tasks/{task}/assignees`はこの実機で500になったため、task本体の`assignees`を参照し、割当は`PUT /tasks/{task}/assignees`を使った。

## バックアップ証拠

- backup path: Linux user領域の`~/.local/share/pj-general/backups/20260711-113317`
- pj-general: `integrity_check=ok`、restore `ok`、candidates 19件
- Vikunja: `integrity_check=ok`、restore `ok`、tasks 1件
- live DBは上書きせず、別restore-test DBで検証した。

## Hub / Tasks導線の実機確認 2026-07-11

- Hubコンテナを更新し、`GET /api/integrations/vikunja/overview` がVikunja project `Inbox`とtask `#1`を返すことを確認した。
- 概要レスポンスは全1件、未完了0件、完了1件で、期限・担当・Tasks側URLを含む。
- 概要レスポンスへAPI tokenが含まれないことを確認した。
- HTMLへTasks概要、Tasks側リンク、参考ガント表示の導線が配信されることを確認した。
- ブラウザーでのクリック遷移と、Webhook / 再照合後の表示確認は次のユーザーレビュー項目とする。
