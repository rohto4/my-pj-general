# P0運用・backup・rollback runbook 2026-07

## 対象

- Hub: `apps/web`
- Hub DB: `apps/web/data/p0.sqlite` または `P0_DB_PATH`
- Tasks: Vikunja stable `v2.3.0` / API v1
- Vikunja frontend fork: `codex/pj-general-dashboard` / `325bc5475`

secret、token、Cookie、Webhook secretはrepo・SQLite・操作ログへ書かない。

## ローカル起動前確認

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\apps\web\check.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\apps\web\test.ps1
```

既定ポートは4173。別ポートを使う場合だけprocess環境変数 `PORT` を指定する。

## 起動後の最小確認

1. `/api/health` が200で、DB integrityと依存状態を返す。
2. `/api/bootstrap` が200で、候補・source・設定を返す。
3. `/api/observability` が200で、source同期・reconcile・backup世代の結果を返す。
4. `/` と `/chat` がListening Loungeで表示される。
5. Vikunja設定済み環境では `/api/integrations/vikunja/overview` が利用可能になる。
6. Web手入力は、検証用であることを明示した内容だけで試す。
7. GOは実taskを作るため、疎通確認だけならAPI testを使う。

`/api/health` はDBの `quick_check` と件数、Vikunja / local LLMの状態を返す。token、secret、接続URL、DB実体pathは返さない。未設定・明示無効は正常な縮退、設定済みで到達不能または設定不足は `degraded` とする。

## Hub SQLite backup

通常backupはSQLite online backupを使うため、Hubを停止せず取得できる。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\apps\web\backup.ps1 -BackupDir .\tmp\backup\hub
```

結果JSONの `integrity=ok`、`sha256`、`counts` を保存する。wrapperはtimestamp付き世代を追加するだけで、既存backupを自動削除しない。

`tmp`内のbackupは同一ディスク上の一時退避であり、本番backupではない。常設環境は別PC、NAS、外付け媒体などへ複製する。

定期入口同期は `infra/systemd/pj-general-sync.timer` を使う。初回登録後は次でoneshot実行と観測結果を確認する。

```bash
sudo systemctl start pj-general-sync.service
sudo journalctl -u pj-general-sync.service -n 100 --no-pager
curl -fsS http://127.0.0.1:4173/api/observability
```

## Hub SQLite restore

1. Hubを停止する。
2. 現行DBを別名backupする。
3. 復元対象を `P0_DB_PATH` の実体へコピーする。
4. `check.ps1` と `/api/bootstrap` を確認する。
5. Vikunja taskは別正本のため、必要ならreconcileを実行する。

restore前後でDBを削除しない。破損調査用に現行実体を保持する。

## Vikunja backup / restore

VikunjaはDBだけでなく、filesとconfig / secretの復元可能性を確認する。`infra/vikunja/backup-and-verify.py` はDBを別restore-testへ復元し、integrity、対象件数、`execution_links` 件数、backup / restore SHA-256を出力する。Linuxの具体手順は次を正本にする。

- `docs/guide/linux-server-setup-for-vikunja.md`
- `docs/arch/vikunja-linux-deployment-and-operations-2026-07.md`
- Vikunja公式: https://vikunja.io/docs/what-to-backup/

## frontend fork rollback

1. 切替前にVikunjaデータをbackupする。
2. stable `v2.3.0` imageとcustom imageを異なるtagで保持する。
3. custom imageを別portで起動し、login、project、task detail、List / Table / Kanban / Ganttを確認する。
4. reverse proxyまたはcomposeの参照tagだけを切り替える。
5. 異常時はstable tagへ戻す。DB schema変更を伴うunstable upgradeを同時に行わない。

## 障害時の縮退

| 障害 | 維持する機能 | 対応 |
| --- | --- | --- |
| Ollama停止 | Hub、候補、確認待ち、Vikunja | chatだけ接続エラー表示 |
| Vikunja停止 | intake、候補編集、管理 | GOを再試行可能にし、判断を保持 |
| Webhook欠落 | Hub / Tasksの正本分離 | reconcileでmirrorを修復 |
| Slack / Misskey connector停止 | Web / vault / chat入口 | source単位で失敗を記録。Misskeyは既定無効のため、外部取得未実装をHub全体の障害にしない |
| Hub停止 | Vikunjaでのtask実行 | Hub復旧後にreconcile |

## P0 rollback境界

P0 rollbackはHub DBとVikunjaデータを独立して扱う。Hubのcandidate / decisionをVikunja task本文で再構築したり、Vikunja taskをHub候補から上書き再生成したりしない。

## 機能別の復旧後照合

障害復旧、設定変更、再配信の後は、成功応答だけで完了扱いにせず、対象機能の正本データと観測を照合する。実データを変更する確認操作はユーザー確認後だけに行う。

| 機能 | 復旧後に確認する状態 | 合格条件 | 正本 / 自動根拠 |
| --- | --- | --- | --- |
| vault / Slack / Misskey入口 | `/api/observability` の最新`sourceSyncRuns`、candidate件数、Vaultのlineage table件数 | sourceごとのstateとaction / aspiration件数が説明でき、同一source refまたはbatch再送で重複候補が増えない | `docs/spec/ai-candidate-proposal-contract-p0.md`、`docs/spec/intake-source-adapters.md`、`docs/ops/knowledge-vault-ai-intake-runbook-2026-07.md`、`apps/web/test/test_candidate_proposal.py`、`apps/web/test/test_source_sync.py`、`apps/web/test/api.test.mjs` |
| Hub候補・判断 | `/api/bootstrap` の候補、判断ログ、operation ID | 成功した操作だけがHTTP応答・画面ログ・`decisions.note`で一致し、失敗時に仮候補を作らない | `docs/spec/confirmation-queue-p0.md`、`apps/web/test/api.test.mjs` |
| Vikunja連携 | `execution_links`、`execution_task_state`、`sync_attempts`、reconcile結果 | task正本を上書きせず、失敗は再試行可能、削除済みtaskは`detached`として履歴を残す | `docs/spec/vikunja-integration-contract-2026-07.md`、`docs/spec/vikunja-integration-acceptance-tests-2026-07.md` |
| ローカルLLM相談 | `/api/health`、既存thread、候補一覧 | provider障害時もHub/Tasksと既存履歴を保ち、失敗送信が候補/GOを起こさない | `docs/spec/local-llm-chat-runtime-contract-p0.md`、`apps/web/test/api.test.mjs` |

`/api/health` が`degraded`のときは、失敗した依存だけを復旧対象にする。Hub SQLiteが`ok`であれば、VikunjaまたはLLMの一時障害を理由にDB、候補、判断、Taskを削除・再取り込みしない。
