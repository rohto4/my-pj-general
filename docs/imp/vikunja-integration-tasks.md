# Vikunja / pj-general 結合タスクリスト

作成日: 2026-07-10
目的: Vikunjaを実データの実行TODO基盤として接続し、実際の不足を観測したうえでfork/pluginの拡張点を判断する。

## 方針

- 先にupstream無改変で実行する。
- clone、GitHub fork、実行環境は分離して管理する。
- pj-generalの候補・出典・判断履歴を失わない。
- モック候補を連携対象にせず、実在するSQLite候補を使う。
- 機能不足は不足機能一覧へ記録し、plugin / frontend fork / backend forkを後から選ぶ。

## タスク

### A. 設計・記録

- [x] コンポーネント図を作成する
- [x] データフロー図を作成する
- [x] 連携データ設計と冪等性を作成する
- [x] 実装前方針をdiaryに記録する
- [x] 安定版とmainのAPI差分をレビューし、初回releaseを`v2.3.0`に固定する
- [x] 実機受入試験 VJ-001〜VJ-015 を作成する
- [ ] fork / plugin不足機能一覧を作成する

### B. upstream / fork

- [x] Vikunja upstreamを`G:\devwork\clone-dir\vikunja-upstream`へcloneする
- [x] `rohto4/vikunja` GitHub forkを作成する
- [x] upstream remoteとfork originを確認する
- [ ] upstreamのライセンス、release、build手順を記録する
- [x] forkは当面変更せず、差分管理の土台だけ作る

### C. Vikunja実行

- [x] Linux常設サーバーを用意し、Docker Compose実行環境を確認する
- [x] Compose、Vikunja env、pj-general envのSecretなし雛形を作成する
- [x] Windows開発環境ではGo・Docker・WSLがないため、実行方式をLinuxサーバー前提にする
- [x] 実在するVikunja `v2.3.0` serverを起動し、API到達性を確認する
- [x] LinuxユーザーへWindowsのSSH公開鍵を登録する
- [ ] project、ユーザー/API tokenを作成する
- [x] project `1 / Inbox`、ユーザー、runtime API tokenを作成する
- [x] 実データのtaskをAPI作成・画面更新して確認する
- [x] Webhook送信先と署名検証方式を確認し、project webhookを登録する
- [x] private Docker network宛Webhook許可を明示設定し、実配送を完了する

### D. pj-general結合

- [x] Vikunja接続先、公開URL、project ID、token、Webhook secretを環境変数から読む
- [x] `execution_links`、`execution_task_state`、`sync_events`、`sync_attempts`を追加する
- [x] GO時にVikunja taskを作成する
- [x] 同一候補の二重登録を防ぐ
- [x] 作成済みtask URLを確認待ち詳細に表示する
- [x] task更新Webhook receiverと状態反映を実装する
- [x] 実Webhook配送でpj-general反映を確認する
- [ ] 失敗・再試行・外部削除を履歴に残す（失敗・再試行は完了、外部削除は未完）
- [x] Webhook欠落を補う再照合APIで実task状態を修復する
- [x] 外部task 404を`detached`へ反映するintegration testを追加する
- [ ] upstreamのみで足りる範囲を受入テストで固定する

### E. 拡張判断

- [ ] 実際の不足を画面、API、データ、運用に分類する
- [ ] API / Webhook / 外部連携で解決できるものを除外する
- [ ] backend plugin候補を最小実装で検証する
- [ ] frontend fork候補を実画面で検証する
- [ ] backend forkが必要かを最後に判断する
- [ ] fork差分、upstream追随、テスト、ライセンス運用を記録する

### F. 検証・記録・公開

- [x] Node/Pythonの既存P0テストを通す
- [x] adapterのAPI v1 payload、Webhook署名、冪等キーのunit testを追加する
- [x] GO endpointとWebhook endpointのintegration testを追加する
- [x] 実Vikunja向け受入試験仕様を追加する
- [x] 実VikunjaとのE2Eを確認する
- [x] GO、二重作成防止、再照合、再起動、backup/restoreの実Vikunja E2Eを確認する
- [x] 実装前の設計図を作成する
- [ ] 設計図を実装結果に合わせて更新する
- [ ] diaryに設計との差分と実装結果を記録する
- [ ] `docs/imp/imp-comp.md`へ完了単位を追記する
- [x] knowledge-vaultへ汎用化できる知見を反映する
- [x] 設計チェックポイントを`rohto4`でcommit/pushする

## 現時点の実装開始ゲート

Vikunja本体の実データ結合は、Linux常設サーバーまたは同等のDocker/公式バイナリ実行環境が用意されるまで保留する。実行環境なしでVikunja APIを模擬して結合済みとは扱わない。

サーバーが用意されるまでに、設計図、API契約、SQLite migration、テストケース、配置手順、バックアップ・更新手順を先に完成させる。

2026-07-11時点で、設計レビュー、API契約、データモデル、SQLite migration、受入試験、Linux構築手順、Compose/env雛形までは完了した。サーバー非依存で残る主作業はadapterのunit/integration testであり、実機E2EはLinux環境待ちである。

## 仮完了条件

- 実在候補をGOするとVikunjaに1件だけTODOが作られる。
- Vikunja側の完了・期限・担当の変更がpj-generalで確認できる。
- 外部連携失敗でもpj-generalの判断履歴が残る。
- clone、fork、結合コード、設計図、データ設計、diary、完了記録が揃う。
