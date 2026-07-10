# Linux 常設サーバーの定期入口同期アーキテクチャ

作成日: 2026-07-10

## 目的

Linux 常設サーバーで、各入口からタスク候補を6時間ごとに回収し、確認待ちキューへ安全に反映する。

既存の `devwork -> knowledge-vault` 定期収集とは責務を分ける。ここでは `knowledge-vault -> pj-general` を含む、pj-general 側の候補化を扱う。

## 採用方針

- Web サーバーの常駐状態に依存して同期を実行しない。
- `systemd timer` が6時間ごとに単発の同期 worker を起動する。
- Web の手動取り込みと定期 worker は、同じ domain / adapter の同期関数を呼ぶ。
- 初期は単一サーバーの SQLite 運用も許容するが、複数入口・再試行・Vikunja TODO 連携を進める前に PostgreSQL へ移行する。
- 将来は `workers/sync` の常駐 worker と Redis / BullMQ の定期 job へ移せる責務分割にする。

```text
Slack / Misskey / knowledge-vault / Web手入力
                 |
                 v
        source adapter (差分取得・正規化)
                 |
                 v
   candidate pipeline (分類・重複排除・記録)
                 |
                 v
     PostgreSQL または P0 SQLite / 確認待ちキュー
                 |
                 v
             pj-general Web

systemd timer -> pj-general-sync.service -> workers/sync
```

## systemd 運用

- timer: `OnCalendar=*-*-* 00,06,12,18:00:00`
- missed run: `Persistent=true` を有効にし、停止中に逃した回を復帰後に実行する。
- service: `Type=oneshot`。同期の終了コードを systemd journal に残す。
- 排他: `flock` またはDB advisory lockで、前回実行が残っている場合の重複実行を防ぐ。
- secret: `/etc/pj-general/sync.env` など repo 外の環境ファイルまたは systemd credential から与える。
- 実行結果: source ごとの `last_success_at`、取得件数、候補化件数、skip件数、失敗内容を保存する。

## 同期契約

1. source adapter は source event を cursor または content hash で差分取得する。
2. 正規化済み event は `source_id + external_id`、または content hash を一意にして冪等に保存する。
3. candidate 化は event から再実行可能にし、同一 event を重複候補にしない。
4. 入口ごとの失敗は全体同期を止めず、source 単位で記録・再試行する。
5. 手動取り込みは定期同期と同一 lock / 同一冪等キーを使う。

## P0 からの移行

P0 は SQLite と管理画面の手動 `取り込み` を保持する。Linux 常設へ移すときは、先に worker を切り出し、次に systemd timer で起動する。その後に PostgreSQL、Redis / BullMQ、Vikunja TODO 一方向連携を導入する。
