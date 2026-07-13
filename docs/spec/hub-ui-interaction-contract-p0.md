# P0 Hub UI操作契約

## 目的

`Thread Line Hub` の画面操作、画面内状態、Tasksへの導線を、実装の読込み前に確認できるP0仕様として定義する。画面の見た目・ブランド要件は `docs/product/thread-line-workspace-requirements.md`、候補データと判断の意味は `docs/spec/confirmation-queue-p0.md`、Hub / TasksのAPI・正本境界は `docs/spec/vikunja-integration-contract-2026-07.md` を正本とする。

## 画面内ナビゲーション

| 主メニュー | hash | スクロール先見出し | 主な目的 |
| --- | --- | --- | --- |
| ダッシュボード | `#dashboard` | ダッシュボード | 入口、候補、処理、Tasks概要、優先確認、判断ログを横断する |
| 簡易日程 | `#gantt` | 簡易日程 | Tasksの読み取りmirrorを使い、期間・担当・進捗を確認する |
| タスクキュー | `#queue` | タスクキュー | 確認待ち候補を絞込み、詳細を確認し、判断する |
| ワークビュー | `#worker` | ワークビュー | 作業中のTasksとCodex起動支援を確認する |
| 簡易管理 | `#admin` | 簡易管理 | P0の入口、タグ、prompt、scope、role、運用観測を設定する |

- 左レールのリンクは同一ページの相対hashだけを使う。
- hash変更、画面内button、初期表示のいずれも同じscroll処理を使い、対象sectionのscroll marginを尊重する。
- hashに対応するsectionがない場合は、既存の表示状態を壊さず、画面トップへ強制移動しない。
- AI相談は主メニューに置かず、左レール下部の独立buttonからdrawerまたは`/chat`へ開く。未実装の詳細管理は同じbutton骨格で置くが、状態変更を起こさず「準備中」を示す。

## ダッシュボードの状態契約

| 領域 | 正常 | 空 | 読込 | 失敗 | 次の操作 |
| --- | --- | --- | --- | --- | --- |
| 入口別の量 / 候補の種類 | SQLiteの集計 | 0件を表示 | 読込中ラベル | 管理メッセージ | 入口または書き入れを確認 |
| 処理フロー | 候補・未処理・不足・予定化・用意済みTasks | 0を表示 | 読込中 | 管理メッセージ | タスクキューへ移動 |
| Tasks側の概要 | 実Vikunjaの件数・直近task | 0件と作成先の説明 | Vikunja読込中 | 接続失敗理由 | 更新またはTasks設定確認 |
| 優先確認 / 判断ログ | 候補・判断を最新順に表示 | 「まだ判断なし」 | 読込中 | 管理メッセージ | タスクキューへ移動 |

- 入口別の量と候補の種類は、他列の高さに引き伸ばされない固定縦幅の反復リストとする。
- `Tasks側を開く`は、対象ProjectまたはtaskのURLが得られた時だけ有効にする。主導線としてTasks青で強調する。
- HubはTasksのtitle、期限、担当、進捗、完了を編集しない。概要・簡易日程は読み取りmirrorであり、Tasks側で編集する責務を表示する。

## タスクキューの操作契約

| 操作 | 事前状態 | 送信先 | 成功後 | 失敗後 | 実データ変更 |
| --- | --- | --- | --- | --- | --- |
| 書き入れ | drawer入力が妥当 | `POST /api/candidates` | pending候補を選択して表示 | drawer内に理由を表示 | あり |
| 編集して保存 | 候補を選択 | `PATCH /api/candidates/:id` | 一覧・詳細・ログを再読込 | 詳細paneに理由を表示 | あり |
| 保存してGO / GO | ユーザーが確認 | `POST /api/candidates/:id/execution` | decision・execution link・Tasks導線を表示 | 詳細paneに理由を表示 | あり |
| 不要 / アーカイブ | ユーザーが確認 | `PATCH /api/candidates/:id/status` | decisionログを最新順で表示 | 詳細paneに理由を表示 | あり |

- `GO`、`不要`、`アーカイブ`、設定変更、候補作成は、実データと判断ログを変更する前に確認dialogを表示する。
- 操作後の受入では、HTTP応答、画面の`bootstrap.log`、SQLiteの`decisions.note`にある同一operation IDを照合する。
- overviewまたはobservabilityの再取得に失敗しても、成功済みの判断操作の結果表示と判断ログを消さない。
- 候補の表示titleはTODO案を優先する。AI要約・抜粋・タグは候補本文と既存タグマスタを根拠にし、LLMが直接GOしない。

## 管理画面の操作契約

- 有効な設定はタイトル横の`有効`ラベルと`無効化`buttonを表示する。
- 停止中の設定はタイトル横の`停止中`ラベルと`有効化`buttonを表示する。
- 取込可能な設定は`取込`buttonを使い、有効化または無効化buttonと縦に積む。
- 狭い幅では、入口設定、タグマスタ、prompt template、取り込み対象を先行する2列へ置く。role表示とAI確定方針は後段行へ置く。
- debug/SQLite/運用観測/P0ルールは薄いオレンジ背景と銅の左罫線を使い、通常操作面と混同しない。
- 設定変更と取込は実データ変更である。P0受入では操作前の確認を必須とする。

## 受入と実装境界

- 受入の実行順、実機変更の確認欄、スクリーンショットは `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` を正本とする。
- 静的button/link/form対応は `docs/imp/p0-frontend-operation-audit-2026-07-12.md` を根拠にする。
- 実装を読む必要がある場合だけ、`apps/web/index.html`、`apps/web/app.js`、`apps/web/styles.css`、API境界が必要なときだけ`apps/web/server.mjs`と`apps/web/db_tool.py`を対象にする。
- 回帰は`apps/web/test/api.test.mjs`とPythonのDB/Vikunja adapterテストを使用する。画面品質は自動回帰だけで完了扱いにせず、幅別の実機受入を残す。
