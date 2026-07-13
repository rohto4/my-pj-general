# P1完了監査 2026-07-12

P1の完了条件を、ローカルで証明できたもの、設計まで完了したもの、Linux実機または実運用データが必要なものに分けて監査する。未検証の項目を完了扱いにしない。

## 証明済み

| 条件 | 証拠 |
|---|---|
| Hub health / 依存縮退 | `GET /api/health`のNode回帰。DB integrity、Vikunja / LLMの`degraded`を確認 |
| source sync / reconcile / metrics | `source_sync_runs`、`GET /api/observability`、管理画面パネル、Node 20件 |
| SQLite backup | online backup、quick_check、件数、SHA-256、世代ディレクトリ |
| worker冪等 / 失敗分離 / lock | `workers/sync/test_run.py` 4件。knowledge-vault / Slackを連続2回実行 |
| reconcile timer契約 | `workers/reconcile/test_run.py` 2件、15分`Persistent=true` timer |
| backup rotation / restore fixture | backup policy 2件、Vikunja restore fixture 1件 |
| Vikunja guide / empty state | `WorkspaceGuide` / `WorkspaceEmpty`、view別guide、対象unit 24件 |
| Listening Lounge build | frontend stylelint、production build、実データ画面レビューREADME |
| source sync domain分離 | `apps/web/source_sync.py`、domain test 2件、workerから直接利用 |
| PoC dry-run | similarity、partial-auto-confirm、CalendarのDB無変更dry-run |
| auth / PostgreSQL契約 | `docs/spec/auth-resource-action-matrix-p1.md`、`docs/spec/postgresql-migration-dry-run-contract-p1.md` |

## 最新配信artifact

| artifact | SHA-256 |
|---|---|
| Hub bundle | `9AE0C741D645EE1F3CEE3EBC88B8C079DD63A72DC038C6302592C211F2F65EE0` |
| P1 worker / backup / PoC bundle | `6A73873F8D6119F61AC170B0BB3AF5BDAC13B7BD9C5F7BBB8F1B39B880659CD5` |
| Vikunja frontend fork基準 | commit `325bc5475` |

## 未証明

| 条件 | 不足している証拠 | 次の操作 |
|---|---|---|
| custom Vikunja image切替・stable rollback | custom imageのLinux buildまでは完了。起動切替・rollback・件数比較が未実施 | `switch-image.sh`を両方向で実行し、task IDとlinkを比較 |
| Linux timer / backup / restore | journal、世代、別場所restoreの実DB件数/hash/link | bundle展開後にsystemdを有効化し、2回分のjournalを保存 |
| Hub停止→reconcile回復 | LinuxでHub停止、Vikunja継続、復旧後一致の実証 | Hubだけを停止してtask状態を変更し、timer/APIで再照合 |
| custom→stable rollback | custom image起動、stable復帰後の実DB比較 | `switch-image.sh`を両方向で実行し、task IDとlinkを比較 |
| 実運用PoC最終判定 | decision / GO /不要 /完了 /実行linkが不足 | 実データを1巡回してから採用・保留・対象外を再判定 |
| PostgreSQL migration dry-run | 一時PostgreSQLでの移行前後比較 | 導入ゲート発生後に契約手順を実行 |

## 2026-07-12 Linux実機更新

- SSH公開鍵登録後、`unibell4@universe`への接続とDockerグループを確認した。
- 最新Hub/P1/Vikunja bundleを転送し、3 bundleのSHA-256一致を確認した。
- 実DBの再起動前後でHub candidates `19`、decisions `2`、execution links `2`、Vikunja tasks `2`を確認した。データ消失はなく、再インポートは実施していない。
- Hub/VikunjaのDB、files、configを含むbackup/restore drillを実行し、Hub `candidates=19` / `execution_links=2`、Vikunja `tasks=2`、backup/restore hash一致を確認した。
- Hubは最新bundleから再build・再作成し、Vikunja stable `v2.3.0`とともに再起動した。Hub healthはDB/Vikunja `ok`、Ollama未接続で`degraded`。observabilityにHub backup世代が表示された。
- custom Vikunja imageはLinuxでbuild済み。起動切替・stable rollback、systemd timer登録、外部mirror、Hub停止→reconcile回復は未完了。

## 現在の判定

P1は未完了。LinuxのHub再配信と実DB restore drillは完了したが、custom Vikunja imageの無損失rollback、systemd timer、reconcile回復、外部mirror、実運用データを用いたPoC最終判定が残っている。公開鍵や秘密情報はリポジトリへ保存しない。
