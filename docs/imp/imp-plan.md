# 実装方針

## P0: 契約実証

完了。Hubの入口・候補・判断と、Vikunjaの実行TODOを一方向で接続し、状態mirror、AI相談、管理、Listening Loungeを実証した。

## P1: 常設運用と観測

1. backup / restore / health / reconcileを運用可能にする。
2. Vikunja frontend forkをrollback可能に配信する。
3. 定期入口workerをknowledge-vaultから導入する。
4. 実運用の判断・GO・完了データを蓄積する。
5. Misskey、重複束ね、部分自動確定、Calendarを小さくPoCする。
6. PostgreSQL、認証、queueは観測した導入ゲートに従う。

詳細は `docs/product/p1-phase-brief-2026-07.md` と `docs/imp/p1-implementation-tasks-2026-07.md` を正本とする。
