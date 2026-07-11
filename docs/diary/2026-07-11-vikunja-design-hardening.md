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

## 2026-07-11 実機到達確認

- LAN上の実サーバー`/api/v1/info`からVikunja `v2.3.0`の正常応答を確認した。private IPはリポジトリへ記録しない。
- Webhook有効、local認証有効で、初回設計のAPI v1対象と一致している。
- SSH host名`universe`はWindows側で名前解決できなかった。
- LAN上の実サーバーには到達したが、初回は公開鍵未登録のため認証に失敗した。その後、専用SSH鍵を登録して接続済み。

## 2026-07-11 実装結果

- pj-generalを`Node 24 + Python + SQLite`コンテナとしてLinuxへ配置し、LAN上の`4173`で起動した。
- ローカルの実SQLite候補19件をサーバーへ移し、候補`KV-e378384856`をGOした。
- Vikunja project `1 / Inbox`へtask `#1 / L1 Triggers`が実作成され、候補ID、出典、TODOが説明へ入った。
- 同じ候補を再GOしてもtask IDは`1`のまま、`execution_links`も1件で、二重作成されないことを確認した。
- Webhook `#1`を`task.created / task.updated / task.deleted`で登録した。
- Vikunjaでtask `#1`を完了し、配送イベント生成まで確認した。
- 実配送はVikunjaのSSRF保護がDocker private IPを拒否して停止した。`VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS=true`の明示承認後に再試験する。
- Webhook欠落を補う再照合APIを追加し、実task `#1`の完了状態をpj-generalへ修復した。
- 両SQLiteをonline backupし、別ファイルへrestoreしてintegrityと件数を確認した。
- Vikunjaとpj-generalを再起動し、候補19件、link 1件、done状態の永続化を確認した。

### 設計との差分

- API用URLとブラウザー用URLは同一と想定していたが、Docker内部通信では`VIKUNJA_BASE_URL`と`VIKUNJA_PUBLIC_URL`の分離が必要だった。
- ホストにはNodeを導入せず、pj-general専用コンテナへPythonを同梱した。
- 初回データベースは設計どおりSQLiteを使用し、Vikunjaとpj-generalで別ファイルを正本にした。
- systemd workerは未導入だが、定期実行から呼べる再照合HTTP endpointを先に実装した。
- 次のゲートはSSH公開鍵登録とVikunja API token発行。project IDはtoken取得後にAPIから特定する。
