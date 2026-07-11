# 2026-07-11 Hub / Tasks導線結合

## 実施したこと

- HubにVikunja API v1のproject取得とproject tasks取得を追加した。
- HubダッシュボードにTasks側の全件数、未完了、完了、直近タスクを表示する読み取りProjectionを追加した。
- Tasks側プロジェクトへのナビゲーション、ダッシュボードリンク、確認待ち詳細リンク、参考ガントリンクを追加した。
- GO後はTasks側で実行タスクを完結し、Hubは入口・候補・判断・対応リンク・状態ミラーを担当する一方向境界へ整理した。
- 概要APIのtoken非露出、未接続・接続失敗表示、既存GO/Webhook/再照合との結合テストを追加した。
- Hub / Vikunjaのデザイン洗練を後続タスクとして `docs/imp/hub-vikunja-ui-harmonization-tasks.md` に分離した。
- Vikunja `v2.3.0`の配信CSSを確認し、Hubを青 `#126cfd`、白・シルバー、黒寄りの文字、明確な境界線の2段階デザインへ調整した。

## 検証

- `apps/web/check.ps1` 成功。
- Nodeテスト10件、Pythonテスト3件が成功。
- 概要APIのテストではproject title、Task件数、直近Task、公開URL、token非露出を確認した。
- 実画面ではダッシュボードのTasks概要と、確認待ちQueueのTasks側リンクを確認した。

## 次の復帰入口

1. `docs/imp/user-tasks.md` のHub / Tasks結合確認を実機で行う。
2. Linux上のHubコンテナへ反映し、`/api/integrations/vikunja/overview` と画面遷移を確認する。
3. データ・導線が問題なければ `docs/imp/hub-vikunja-ui-harmonization-tasks.md` の第1段階へ進む。
