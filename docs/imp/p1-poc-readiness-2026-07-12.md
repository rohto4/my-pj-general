# P1 PoC readiness 2026-07-12

## 現在の実運用データ

ローカルHub SQLiteの`GET /api/observability`相当を確認した。

| 指標 | 現在値 |
|---|---:|
| candidates | 19 |
| pending | 19 |
| source: knowledge-vault | 19 |
| kind: TODO / 検討 / 予定候補 | 14 / 3 / 2 |
| missing candidates | 19 |
| decisions | 0 |
| execution links | 0 |
| Tasks完了mirror | 0 |
| GO率 | 未定義 |

## 暫定判定

これはP1 PoCの最終判定ではなく、実運用データがまだPoC開始ゲートに達していないことを明示するための暫定判定である。

| PoC | 暫定状態 | 根拠 | 開始条件 |
|---|---|---|---|
| Misskey read-only | 保留 | REST / Streaming / Webhookの比較設計は済みだが、接続・取得実績がない | read-only取得を1回実行し、source run / failureを観測する |
| 類似候補提示 | 保留 | decisionsが0件で判断ラベルがない | 同種候補の編集・GO・不要を蓄積し、提示のみを評価する |
| 部分自動確定dry-run | 保留 | GO率が未定義、全候補に不足項目がある | missingなしの対象segmentと誤確定0件のdry-run証跡 |
| Calendar一方向event | 保留 | schedule候補はあるがGO・外部linkがない | ユーザーGO 1件とidempotency keyを検証する |
| PostgreSQL migration | 保留 | lock競合・規模ゲート未到達 | SQLiteの同時書込みまたは規模ゲートを観測する |
| 認証resource-action | 設計継続 | 二人目利用者が未導入 | resource-action matrixを作成し、公開前に再判定する |

## dry-run実績

- 類似候補提示: 19候補から4組を提示。最高score `0.75`。DB書き込みなし。
- 部分自動確定: eligible `0`、blocked `19`、wouldUpdate `0`。全件が`confidence=medium`かつmissingありのため、GOを迂回しない結果になった。
- Calendar一方向event dry-run: 現在のapproved候補は `0` 件のため `wouldCreate=0`、`externalCalls=0`。Google Calendarへの書き込みは行っていない。approvedかつ日付・所要時間を持つ候補が作成された後に、同じ`gcal-...` idempotency keyで再実行検証を行う。

## 次に集める証拠

1. 確認待ち候補を編集・GO・不要・アーカイブで最低1巡回し、decision countsを作る。
2. GO済みVikunja taskを1件作り、完了Webhookとreconcileの両方を観測する。
3. workerを同一入力で2回実行し、source runのcursor・created・skippedを保存する。
4. 上記データが揃った後に、各PoCを採用・保留・対象外の最終判定へ昇格する。
