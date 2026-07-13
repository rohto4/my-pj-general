# 次セッションの焦点

> セッションを切り替える場合は、まず `docs/diary/2026-07-12-session-handoff.md`、`docs/diary/2026-07-12-resume-prompt.md`、`docs/diary/2026-07-13-design-documentation-coverage-handoff.md`を読む。完成度の星取表は `docs/imp/p0-p1-completion-assessment-2026-07-12.html`、設計書の読込境界は `docs/imp/design-documentation-coverage-assessment-2026-07-13.html`、次の目標は `docs/imp/next-goal-p0-frontend-completion-2026-07-12.md`を正本とする。

## 現在地

- P0バックエンド・連携契約は完了。P0フロントはRV01〜RV05の完成度レビュー、U03/U04/U05最終受入、Thread Line画像調整が残るため正式完了ではない。
- Hub本流はListening Lounge。
- Vikunja frontend forkは `codex/pj-general-dashboard` / `325bc5475`。
- Hub回帰はNode 28件、Python 7件成功。P1のworker / backup / PoC回帰はP0完了後に再開する。
- P1ブリーフと実装タスクに沿って、P1-A観測・backup雛形、P1-C worker / timer、P1-B build / switch契約までローカル実装済み。
- Linux配信bundleを転送し、Hubを最新bundleから再build・再作成、Vikunja stableとともに再起動した。DB/files/configの実DBrestore drillも完了。custom Vikunja image、systemd timer、reconcile、外部mirrorはsudo作業待ち。
- P1-Aのsource同期・reconcile・backup観測は、`source_sync_runs`、`GET /api/observability`、管理画面パネルまでローカル実装・回帰済み。
- P1-Cのoneshot worker / systemd timer雛形は `workers/sync/` と `infra/systemd/` に追加済み。Linuxでの初回timer実行と連続2回の実機証跡が残作業。
- P1-Aのreconcile timer、運用metrics、backup rotation雛形、P1 PoC暫定判定、Calendar dry-run、認証/PostgreSQL設計契約も追加済み。Linux実機の配信・restore・実運用データ収集が次の焦点。

## 再開時に読むもの

1. `docs/guide/implementation-context-reading-guide.md`で対象役割を選ぶ。
2. `docs/imp/design-documentation-coverage-assessment-2026-07-13.html`の対象行から正本文書を最小読込する。
3. P0受入では`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`の赤・黄の先頭から進める。
4. P1の再開が承認された場合だけ、`docs/product/p1-phase-brief-2026-07.md`、`docs/imp/p1-implementation-tasks-2026-07.md`、`docs/ops/p0-operations-runbook-2026-07.md`を追加で読む。

## 次の焦点

P1実機運用へ進む前に、P0フロント受入追加タスク（`docs/imp/p0-frontend-completion-tasks-2026-07-12.md`）を実行する。画面の全操作、読み取り専用責務、無効状態、最新データ反映を受入し、RV01〜RV05の黄色枠レビューを上から完了させてからP1へ戻る。

セッション2で、`docs/imp/p0-frontend-operation-audit-2026-07-12.md` に静的操作監査を追加し、Hubの責務・状態mirror・未接続/接続失敗表示を実装した。次は4173番を現行ソースへ置換した実画面で、Hub操作、実Vikunja、1280 / WQHD / 4K縦3分割の証跡を取得する。4199番の現行APIは200を確認済みだが、アプリ内ブラウザから到達できなかったため、旧4173番プロセスを勝手に停止しない。

Linuxの次回起動は、既存の分離Composeではなく`infra/deploy/`を統一入口として配置する。`start-pj-general.sh --dry-run`でfork bundle・custom image・非secretパスを確認してから一式起動し、Listening Lounge版Vikunjaが正本imageであることを`docker inspect`で確認する。

常設運用・観測とVikunja fork配信のローカル契約は完了。次はLinux実機での配信、timer連続2回、backup/restore、custom→stable rollbackを実施する。PostgreSQL、認証、部分自動確定は実運用ゲートを満たすまで先行しない。

## Linux配信の再開入口

1. `docs/guide/linux-listening-lounge-deploy.md` を読む。
2. `tmp/pj-general-web-working-tree.tgz` と `tmp/vikunja-listening-lounge-working-tree.tgz` のhashを確認する。
3. Linux側でVikunja custom imageを別tagでbuildし、stable rollbackを確認する。
4. systemd sync / backup / reconcile timerを登録し、2回分のjournalとHub停止→復旧証跡を取得する。
