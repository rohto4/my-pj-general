# 2026-07-10 Vikunja / pj-general 結合開始記録

## 目的

Vikunjaのクローン、GitHub fork、pj-generalとの実データ結合を進め、実際の画面・操作・データ保持を確認したうえで、fork/pluginの拡張点を判断できる状態にする。

## 開始時点の確認

- pj-generalは`0bbd027`までGitHubの`rohto4/my-pj-general`へpush済み。
- `apps/web`はSQLiteの実データを表示するP0本デモである。
- 現在のGOはpj-general内の候補状態変更までで、Vikunjaへの実登録は未実装。
- 既存方針は、Vikunja upstream無改変を先に試し、不足を観測してからplugin / frontend fork / backend forkを判断すること。
- Windows側の標準PATHにはGo、Docker、WSLがない。ソースcloneと実行方式を分離する。

## 2026-07-10 方針変更

Windows開発環境からVikunja本体を実データで起動できないため、モックAPIで結合済みと扱わない。Linux常設サーバーまたは同等の実行環境が用意されるまでは、設計・契約・データ設計・運用手順を先に完成させる。

upstream cloneは`G:\devwork\clone-dir\vikunja-upstream`へ完了した。GitHub fork `https://github.com/rohto4/vikunja`を作成し、cloneの`origin`へ設定した。upstreamとforkのremoteを分離している。
upstream cloneの確認commitは`e992ed594cc39044a55acf1c7b157501d43797f9`。task作成resourceとWebhook payload形をソースから確認した。

設計チェックポイントは`eb172e3`、Webhook契約修正は`5ba24c5`として`rohto4/my-pj-general`へpushした。

## 採用して開始する方針

1. `pj-general`に入口・候補・出典・判断・同期履歴を保持する。
2. VikunjaはGO済み候補の実行TODOとして扱う。
3. `GO -> Vikunja REST API`を最初の実登録経路にする。
4. `Vikunja Webhook -> pj-general`を実行状態の戻し経路にする。
5. 先にupstreamを実行し、標準機能で足りない点を一覧化する。
6. 不足機能一覧を根拠に、plugin / frontend fork / backend forkを選ぶ。

## 参照設計

- コンポーネント図・責務境界: `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
- データ設計・ER図: `docs/data/vikunja-integration-data-design-2026-07.md`
- 実装タスク: `docs/imp/vikunja-integration-tasks.md`
- OSS拡張比較: `docs/candi-ref/vikunja-fork-plugin-assessment-2026-07.md`

## 実装前に残る確認

- upstream clone先とGitHub forkの実体。
- WindowsでのVikunja実行方式。Docker/WSL/Goが利用できないため、公式バイナリまたは別Linux実行環境を検証する。
- Linux常設サーバーのOS、DNS、TLS、PostgreSQL、バックアップ領域。
- Vikunjaのproject/API token/Webhook設定。
- SQLite追加テーブルと既存候補状態遷移の接続点。

## 設計との差分記録欄

実装開始後、以下をこのDiaryへ追記する。

- 実際に採用したVikunja実行方式。
- API/Webhookの実際のpayloadと差分。
- 設計図から変更した責務・データ・状態。
- upstream無改変、plugin、frontend fork、backend forkの最終判断。
- 実データで確認した操作と未解決の不足。
