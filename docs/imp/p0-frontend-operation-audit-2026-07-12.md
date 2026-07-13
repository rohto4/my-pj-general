# P0フロント操作監査 2026-07-12

## 判定範囲

この文書は、P0フロント受入の最初の工程である全button / link / formの静的監査結果である。操作実証の正本は本書、進捗と完了条件は `p0-frontend-completion-tasks-2026-07-12.md`、星取表は `p0-p1-completion-assessment-2026-07-12.html` とする。

| 画面・要素 | 結果 / API | 現在の判定 |
| --- | --- | --- |
| サイドナビ（横断・Tasks概要・確認待ち・相談・作業者・管理） | Hub内anchorまたは`/chat`へ遷移。Tasks概要は外部リンクへ変えない | 静的確認済み |
| 書き入れ / drawer | `POST /api/candidates`。成功時は候補一覧・選択・ログを更新、失敗時は管理メッセージに表示 | Node回帰済み / 実画面待ち |
| 確認待ち詳細の編集・保存 | `PATCH /api/candidates/:id`。title / summary / excerpt / todo / schedule / tagsを保存 | Node回帰済み / 実画面待ち |
| 保存してGO / GO | `POST /api/candidates/:id/execution`。既存linkがあれば同じ外部taskを返す。実行前に実データ・判断ログ変更の確認ダイアログを表示する | API結合回帰済み / 実画面の実データ操作待ち |
| 不要 / アーカイブ | `PATCH /api/candidates/:id/status`。実行前に実データ・判断ログ変更の確認ダイアログを表示する | API結合回帰済み / 実画面の実データ操作待ち |
| Tasks概要の更新 | `GET /api/integrations/vikunja/overview`。正常・未接続・接続失敗・0件を表示 | 未接続表示を実画面確認済み / 実Vikunja待ち |
| Tasks側を開く / 直近task | `project.url` / `task.url`が取得できた場合のみ外部リンクを有効化 | 未接続時のdisabled理由を確認済み / 実Vikunja待ち |
| Tasks連携予定表示 | Hubの読み取りmirror。期限・担当・進捗・完了はTasks側で編集することを明示 | empty表示を確認済み / 実Vikunja待ち |
| AI相談・候補として追加 | `POST /api/chat/messages`、`POST /api/chat/suggestions/:id/accept`。候補化だけで自動GOしない | API結合回帰済み / 実画面待ち |
| 作業者コピー | Clipboard API。失敗時は管理メッセージへ表示 | 静的確認済み / 実画面待ち |
| 管理: 観測更新 | `GET /api/observability` | Node回帰済み / 実画面待ち |
| 管理: Slack payload | `POST /api/import/slack`。JSON配列以外は送信前に止める | 静的確認済み / 実画面待ち |
| 管理: source / prompt / role / AI方針 / scope / tag | 各`PATCH /api/admin/*`または`POST /api/admin/tags` | API境界確認済み / 実画面待ち |

## 無効・読み取り専用の扱い

- 未接続: Tasks側を開くリンクは無効化し、「Vikunjaは未接続です。設定後に更新してください」と表示する。
- 接続失敗: 外部リンクを有効にせず、「Vikunjaへ接続できません。更新して再試行してください」と表示する。
- 読み取り専用: Hubは候補・判断・GOを編集し、Tasks側はtitle・期限・担当・進捗・完了を編集する。Hubの概要・ガント・mirrorはその境界を表示する。
- 0件: Tasks概要とガントは、作るべき固定sampleを出さず、次の操作を説明するempty stateにする。

## 実機証跡の残り

- R03は現行bundleを4173番へ再配信し、`/api/bootstrap` 200、管理画面の状態ラベル・操作列・2列配置・4K縦3分割相当の横崩れなしを確認済み。
- U03の実データ判断操作は未達報告を受領した。現行コードは判断ごとに操作IDを発行し、HTTP応答・画面表示の`bootstrap.log`・SQLite `decisions.note`の`operation:<ID>`を同一操作IDで照合する。observability取得失敗で再描画が止まる経路は修正済み。実データ操作は実行前確認を必要とする。
- RV01〜RV05/U01/U05の画面改善・同一条件証跡は `docs/imp/p0-frontend-completion-tasks-2026-07-12.md` の報告後タスクへ分離した。実データの再インポートは行わない。
