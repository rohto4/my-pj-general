# 2026-07-11 Vikunja設計硬化

## 実施したこと

- Vikunja stable `v2.3.0`とmain cloneのtask API差分を確認した。
- 初回実機結合をstable `v2.3.0` / API v1へ固定した。
- 候補判断、外部同期、外部task状態を別軸へ分離した。
- `execution_task_state`、任意の外部event ID、`dedupe_key`をデータ設計へ追加した。
- 実機受入試験 VJ-001〜VJ-015 を作成した。
- Linux向けComposeと、Vikunja / pj-generalを分離したenv雛形を追加した。
- SQLite migrationをテスト先行で実装し、既存テストを含む8件を通した。
- PowerShellのtest/check wrapperが子プロセス失敗を成功扱いしないよう、終了コードを伝播させた。
- API v1 task作成request、Webhook HMAC検証、外部event ID任意の冪等キーをadapterのunit testへ固定した。

## 現在地

Linuxなしで進められる設計レビュー、起動準備、schema実装は完了した。次のユーザー作業は設計レビューまたはLinuxサーバー準備であり、順序は問わない。

## 実機待ち

- Vikunja `v2.3.0`コンテナ起動
- project、API token、Webhook作成
- GO adapterとWebhook receiverの実API疎通
- VJ-001〜VJ-015の証拠採取
- 実測した不足に基づくfrontend fork / plugin / backend fork判断

## 再開入口

- `docs/imp/vikunja-design-review-2026-07-11.md`
- `docs/spec/vikunja-integration-acceptance-tests-2026-07.md`
- `docs/guide/linux-server-setup-for-vikunja.md`
- `docs/imp/vikunja-integration-tasks.md`
