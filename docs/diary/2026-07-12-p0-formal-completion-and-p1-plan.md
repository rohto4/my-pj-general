# 2026-07-12 P0正式完了・P1計画 handoff

## 到達点

- P0を正式完了と判定した。
- Hub / Vikunja / AI相談 / 管理 / 実入口の現行正本を実装へ同期した。
- Listening Lounge本流とVikunja fork最終commit `325bc5475` を完了証跡へ反映した。
- P0運用・backup・rollback runbookを作成した。
- P1の候補評価、フェーズブリーフ、優先順位付きタスク、受入条件を作成した。

## 今回の実証

- Hub check成功。
- Node test 14 / 14成功。
- Python unittest 3 / 3成功。
- Hub `http://127.0.0.1:4173/`、`/chat`、`/api/bootstrap`、Vikunja概要APIが200。
- 実DBは候補19、source 5、execution link 0、chat source有効。
- Listening Lounge属性を通常URLで確認した。
- GO / Webhook / 再照合の実機証跡は `docs/imp/vikunja-integration-verification-2026-07-11.md` を再確認した。

## 重要な判断

- 現在の19候補・判断0・execution 0という運用量では、PostgreSQLや認証を先に入れない。
- P1は常設運用・観測、fork配信、定期workerの順とする。
- Misskey、重複束ね、部分自動確定、Calendarは実運用データ取得後のPoCとする。
- P1初期はSQLiteを維持し、複数writer、認証、規模、lock競合を移行ゲートにする。

## 再開入口

1. `docs/product/p1-phase-brief-2026-07.md`
2. `docs/imp/p1-implementation-tasks-2026-07.md`
3. `docs/candi-ref/p1-candidate-evaluation-2026-07.md`
4. `docs/ops/p0-operations-runbook-2026-07.md`

## 外部ナレッジ評価

今回の成果はP1のPJ固有優先順位と完了監査が中心であり、既存のdocs正本分離・Vikunja境界ルールを超える新しい横断正本は作らない。knowledge-vaultへの追加反映は行わない。
