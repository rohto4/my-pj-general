# P0 本デモ化タスク表

作成日: 2026-07-10

## 目的

P0 薄く実装 1 版を、単なる mock 画面ではなく、薄い機能でも実際にデモできる状態へ進める。

ここでの「本デモ化」は、本番運用の全機能を作る意味ではない。入口、永続化、確認待ち、GO / 編集 / 不要 / アーカイブ、管理画面の最小設定、横断ダッシュボード、ガント表示が、同じデータを使って動く状態を指す。

## 基本方針

- 外部 DB サーバは使わず、P0 は SQLite を第一候補にする。
- md ファイルは handoff、設定説明、docs には向くが、確認待ちキュー、状態遷移、フィルタ、集計、履歴には SQLite のほうが筋が良い。
- SQLite は後続の PostgreSQL 移行を見据え、テーブル境界とフィールド名を雑にしない。
- Slack `memo-ideas`、knowledge-vault は実データ入口の対象にする。Misskey は当面 mock / 後続扱い。
- UI は今のブルーを基調に、明暗・濃淡で操作可能、選択中、操作不能を分ける。不要な角丸は減らす。

## P0 完了条件

| ID | タスク | 完了条件 | 状態 |
| --- | --- | --- | --- |
| P0-DEMO-01 | 横断ダッシュボードを高密度配置へ組み替える | ユーザー指定の配置方針に沿い、WQHD で横断ダッシュボードからガント先頭までが概ね 1 画面に入る | 完了 |
| P0-DEMO-02 | サマリバーを左 1/4 程度に圧縮する | 入口別の量、候補の種類などのサマリが左側の細い列または同等密度で収まる | 完了 |
| P0-DEMO-03 | 確認待ちキュー詳細を作り込む | `AI要約`、`抜粋`、`TODO案` などのタイトルと本文が色・濃淡で明確に分かれる | 完了 |
| P0-DEMO-04 | 操作可能 / 選択中 / 操作不能の色分けを整理する | ボタン、選択行、無効状態、表示専用領域が派手すぎず判別できる | 完了 |
| P0-DEMO-05 | 不要な角丸を減らす | 操作部品以外の過剰な丸角を抑え、業務ツールとして締まった見た目にする | 完了 |
| P0-DEMO-06 | 管理画面の最小範囲を P0 完了状態へそろえる | 入口、タグ、ロール、プロンプトテンプレート、取り込み対象、回収間隔、AI確定方針を確認・編集できる見た目と状態を持つ | 完了 |
| P0-DEMO-07 | SQLite 永続化の最小 schema を作る | candidates、sources、tags、decisions、settings、prompt_templates、gantt_tasks の最小テーブルがある | 完了 |
| P0-DEMO-08 | Web 書き入れ口を SQLite に接続する | 入力した候補が永続化され、リロード後も確認待ちキューに残る | 完了 |
| P0-DEMO-09 | knowledge-vault 入口を実データ読み取りへ寄せる | 対象ディレクトリから候補を生成し、SQLite に取り込める | 完了 |
| P0-DEMO-10 | Slack `memo-ideas` 入口を実データ連携候補へ寄せる | connector / API / 手動import のどれでP0実装するか決め、少なくともデモ可能な取り込み経路がある | 完了 |
| P0-DEMO-11 | 確認待ち操作を永続化する | `GO` / `編集` / `不要` / `アーカイブ` が状態と判断ログへ反映される | 完了 |
| P0-DEMO-12 | ダッシュボードとガントを SQLite 集計に接続する | 表示数値、優先確認、ガントタスクが永続データから描画される | 完了 |
| P0-DEMO-13 | P0 デモ用の起動・確認手順を整える | `pnpm dev` で起動し、初期DB作成、seed、動作確認が迷わず実行できる | 完了 |
| P0-DEMO-14 | docs を更新する | 仕様、実装タスク、完了記録、ユーザー確認事項が更新される | 完了 |

## 管理画面 P0 最小範囲

| 領域 | P0 で見たいもの | P0 で編集したいもの |
| --- | --- | --- |
| 入口設定 | Web / Slack `memo-ideas` / knowledge-vault / Misskey mock | 有効 / 無効、表示名、取り込み対象、最終取り込み時刻 |
| knowledge-vault | records、inbox、memory L1-L2 などの対象 | 対象パス、除外パス、取り込み種別 |
| Slack | `memo-ideas` channel | channel id、取り込み方式、回収間隔 |
| タグ | 初期タグ、AI付与タグ、ユーザー編集タグ | タグ名、カテゴリ、表示色、非表示 |
| ロール | Owner、外部協力者 | 閲覧範囲、GO可能か、schedule中心表示か |
| AI確定方針 | P0は全件確認待ち | P0完了後の部分自動確定候補 |
| プロンプトテンプレート | Codex起動支援、候補整理、GO後作成 | 名前、本文、対象種別 |

## SQLite 初期 schema 候補

| table | 目的 |
| --- | --- |
| `sources` | Web、Slack、knowledge-vault、Misskey mock などの入口 |
| `candidates` | 確認待ちキューの中心データ |
| `candidate_tags` | 候補とタグの対応 |
| `tags` | タグマスタ |
| `decisions` | GO / 編集 / 不要 / アーカイブなどの判断ログ |
| `settings` | P0 管理画面の key-value 設定 |
| `prompt_templates` | Codex起動支援などのテンプレート |
| `gantt_tasks` | ガント表示用のタスク、期間、担当、進捗、依存 |

## ユーザー判断が必要になりそうな点

- Slack `memo-ideas` を P0 で直接 connector から読むか、export / 手動import で始めるか。
- SQLite ファイルの置き場所を `apps/web/data/p0.sqlite` にするか、repo 直下 `data/p0.sqlite` にするか。
- P0 の初期 seed に、実データをどの程度含めるか。
- P0完了後に部分自動確定へ進む条件。

## 実装順

1. UI仕上げ: 横断ダッシュボード配置、詳細pane、管理画面P0項目、色分け、角丸整理。
2. SQLite土台: schema、seed、読み書き API または local server endpoint。
3. Web書き入れ口永続化: 入力、確認待ち表示、状態遷移。
4. knowledge-vault取り込み: 対象パス読み取り、候補生成、重複回避。
5. Slack `memo-ideas` 取り込み: P0方式を決めて実装。
6. ダッシュボード / ガント集計: 永続データへ接続。
7. P0デモ手順とdocs更新。

## 2026-07-10 実装メモ

- `apps/web/db_tool.py` を追加し、Python 標準 `sqlite3` で `apps/web/data/p0.sqlite` を初期化する。
- `apps/web/server.mjs` に `/api/bootstrap`、`/api/candidates`、`/api/candidates/:id/status`、`/api/import/knowledge-vault`、`/api/import/slack` を追加した。
- `apps/web/app.js` は `/api/bootstrap` から candidates / sources / tags / prompt_templates / gantt_tasks を読み込む。
- Web 書き入れ口は `/api/candidates` へ POST し、リロード後も SQLite に残る。
- `GO` / `編集` / `不要` / `アーカイブ` は `/api/candidates/:id/status` で永続化し、`decisions` に判断ログを残す。
- knowledge-vault は `G:/knowledge-vault` の `inbox`、`records`、`tasks`、`memory` から Markdown をスキャンし、`KV-*` 候補として取り込む。
- Slack `memo-ideas` は connector 読み取りで現時点の対象メッセージがないことを確認した。P0では `/api/import/slack` に connector / 手動 import payload を渡す方式にした。
- `pnpm check` は `app.js`、`server.mjs`、SQLite bootstrap を確認する。
