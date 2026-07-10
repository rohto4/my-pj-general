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
- [ ] fork / plugin不足機能一覧を作成する

### B. upstream / fork

- [x] Vikunja upstreamを`G:\devwork\clone-dir\vikunja-upstream`へcloneする
- [x] `rohto4/vikunja` GitHub forkを作成する
- [x] upstream remoteとfork originを確認する
- [ ] upstreamのライセンス、release、build手順を記録する
- [x] forkは当面変更せず、差分管理の土台だけ作る

### C. Vikunja実行

- [ ] Linux常設サーバーを用意する、または実行環境を選択する
- [x] Windows開発環境ではGo・Docker・WSLがないため、実行方式をLinuxサーバー前提にする
- [ ] 実在するVikunja serverを起動する
- [ ] project、ユーザー/API tokenを作成する
- [ ] 実データのtaskを手動で作成・更新して画面を確認する
- [ ] Webhook送信先と署名検証の方式を確認する

### D. pj-general結合

- [ ] Vikunja接続先を環境変数またはSQLite設定から読めるようにする
- [ ] `execution_links`、`sync_events`、`sync_attempts`を追加する
- [ ] GO時にVikunja taskを作成する
- [ ] 同一候補の二重登録を防ぐ
- [ ] 作成済みtask URLを確認待ち詳細と作業者画面に表示する
- [ ] task更新Webhookを受け、pj-generalへ反映する
- [ ] 失敗・再試行・外部削除を履歴に残す
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
- [ ] 連携APIのunit/integrationテストを追加する
- [ ] 実VikunjaとのE2Eを確認する
- [x] 実装前の設計図を作成する
- [ ] 設計図を実装結果に合わせて更新する
- [ ] diaryに設計との差分と実装結果を記録する
- [ ] `docs/imp/imp-comp.md`へ完了単位を追記する
- [x] knowledge-vaultへ汎用化できる知見を反映する
- [x] 設計チェックポイントを`rohto4`でcommit/pushする

## 現時点の実装開始ゲート

Vikunja本体の実データ結合は、Linux常設サーバーまたは同等のDocker/公式バイナリ実行環境が用意されるまで保留する。実行環境なしでVikunja APIを模擬して結合済みとは扱わない。

サーバーが用意されるまでに、設計図、API契約、SQLite migration、テストケース、配置手順、バックアップ・更新手順を先に完成させる。

## 仮完了条件

- 実在候補をGOするとVikunjaに1件だけTODOが作られる。
- Vikunja側の完了・期限・担当の変更がpj-generalで確認できる。
- 外部連携失敗でもpj-generalの判断履歴が残る。
- clone、fork、結合コード、設計図、データ設計、diary、完了記録が揃う。
