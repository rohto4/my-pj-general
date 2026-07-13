# P1 verification matrix 2026-07-12

P1の完了判定を、ローカル証跡とLinux実機証跡に分けて管理する。

| 要件 | ローカル証跡 | Linux実機 | 状態 |
|---|---|---|---|
| Hub / Ollama / Vikunja health | `/api/health`、Node回帰 | 常設URLのHTTP確認。Hub/DB/Vikunjaはok、Ollamaは未接続でdegraded | 実機確認済み / Ollama接続は未設定 |
| source sync / metrics | `source_sync_runs`、`/api/observability` | timer連続2回 | ローカル完了 / 実機待ち |
| Hub backup | online backup、quick_check、SHA-256 | 世代保持・Hub observability alias | 実機確認済み / mirror未設定 |
| Vikunja restore | fixture DB restore-test、件数・link・hash | DB / files / config実データ | 実機確認済み |
| Hub復旧後reconcile | worker / timer契約、API回帰 | Hub停止→復旧→mirror一致 | ローカル完了 / 実機待ち |
| Listening Lounge fork | build / switch / rollback scripts | custom image build済み。custom tag起動・stable rollbackは未実施 | build確認済み / 切替・rollback待ち |
| 配信bundle integrity | Hub `9AE0C741D645EE1F3CEE3EBC88B8C079DD63A72DC038C6302592C211F2F65EE0` / P1 `6A73873F8D6119F61AC170B0BB3AF5BDAC13B7BD9C5F7BBB8F1B39B880659CD5` | Linux `sha256sum`一致後に展開 | 実機確認済み |
| 主要画面UX | 1280 / 1920 screenshots、unit tests | Linux custom image | ローカル完了 / 実機待ち |
| PoC判定 | readiness暫定保留 | 実運用データ後に最終判定 | 暫定保留 |
| Calendar一方向event | dry-run（approved 0、外部call 0、idempotency test） | GO済み候補1件で外部書き込み前の再実行 | 実運用データ待ち |
| 認証resource-action | matrix設計済み | 二人目利用者・共有範囲・競合の観測 | 設計継続 |
| PostgreSQL migration | 移行契約・rollback境界設計済み | 一時PostgreSQLで件数/hash/外部ID一致 | 実DB待ち |

## 実機完了に必要な証跡

1. `sudo docker ps` のimage tagとhealthcheck。
2. Hub `/api/health` / `/api/observability` のレスポンス保存。
3. sync / backup / reconcile timerのjournalと2回分のrun。
4. restore-testの件数、`execution_links`、manifest hash。
5. custom image表示確認後、stable imageへ戻した同じ件数・linkの確認。

## 2026-07-12 Linux実機証跡

- SSH公開鍵認証とDockerグループを確認し、`unibell4@universe`から操作できる状態にした。
- Hub / P1 / Vikunja bundleのsha256がWindows側manifestと一致した。
- 配信前の実データはHub candidates `19`、decisions `2`、execution links `2`、Vikunja tasks `2`。実データ消失は確認されなかったため、重複防止のため再インポートは行っていない。
- `backup-and-verify.py`を実DBに実行し、Hub `candidates=19` / `execution_links=2`、Vikunja `tasks=2`、両方`backup=ok restore=ok`、backup/restore SHA-256一致を確認した。
- `rotate-and-mirror.sh`を実行し、Vikunja files/configと`manifest.sha256`を含む世代を作成した。Hub observability用`p0-20260711-220410.sqlite`も生成した。
- Hubを最新bundleから再build・再作成し、Vikunja stable `v2.3.0`とともに再起動した。`/api/health`はDB/Vikunja `ok`、Ollama未接続による`degraded`、`/api/observability`はbackup世代と19候補/2 linkを返した。
- custom Vikunja image `rohto4/vikunja:2.3.0-pj-general-listening-lounge` はLinuxでbuild済み。Vikunja stableは稼働継続中で、custom tagへの切替・stable rollback・systemd timerの`/etc`登録は未実施。
