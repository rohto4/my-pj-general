# Leantime 採用形態・UI 参照調査

調査日: 2026-07-10

## 結論

Leantime は、TODO リストだけでなく、同じタスクを list / table / kanban / calendar / gantt で扱える。したがって、`pj-general` の確認待ちキューで人が GO した後の「実行するタスク」の置き場兼ビューとして使える。

ただし、現時点で直接フォークして本体開発の土台にすることは推奨しない。Leantime 本体は AGPLv3 であり、ネットワーク越しに提供する改変版にはソース公開義務が及び得る。まずは UI / 情報設計の参照、または独立サービスとしての連携に留める。

推奨順:

1. Leantime の画面を UI / 体験参照にし、`pj-general` は独立実装する。
2. Linux 常設サーバー上に Leantime を独立配置し、GO 済み候補だけを Leantime の TODO に連携する。
3. AGPL の公開条件を受け入れる意思決定とライセンス確認を行った場合だけ、Leantime を fork / 改変する。

## 使える主な機能

| 機能 | Leantime の役割 | pj-general での使い方 |
| --- | --- | --- |
| To Dos / Subtasks / Dependencies | タスク、無制限のサブタスク、依存関係を管理する | GO 後の実行タスクを置く。`AIRegistrationCandidate` との対応IDを持つ |
| List / Table / Kanban | 同じ TODO の見せ方を用途別に切り替える | タスクリストの主画面、個人作業用の軽量ボードを任せる |
| Milestone / Gantt | マイルストーンに紐づくタスクをタイムラインで表示する | ダッシュボードから外部ガントを開く。P0 の簡易ガントを置き換える候補 |
| Calendar / Timeboxing | 計画済みの TODO、予定、マイルストーンをカレンダーで扱う | `ScheduleCandidate` の確認後に計画を確認する画面として利用する |
| Goals / Metrics | 目標、KPI、Goalboard を扱う | P0 以後に、タスクの目的・成果指標を置く候補 |
| Project dashboard / Reports | PJ の状態、進捗、レポートを可視化する | 協力者向け PJ 単位の実行状況を表示する候補 |
| Timesheets / Timer | 作業時間の記録と集計 | 実績管理が必要になった時だけ導入する。P0 対象外 |
| Ideas / Docs / Wiki | アイデア、文書、ナレッジを PJ に紐づける | UI は参照するが、入口・knowledge-vault は `pj-general` 側を正本に保つ |
| Roles / project permissions / 2FA / LDAP/OIDC | 利用者とプロジェクトごとのアクセスを管理する | 外部協力者を Leantime に入れる場合の補助。PJ のロール正本を置き換えない |
| API / plugin / MCP | JSON-RPC API、プラグイン、MCP による拡張 | GO 後の TODO 作成、状態読取、Codex 操作の連携候補 |

Leantime の定期処理も別途必要になる。Linux へ自己ホストする場合は、`pj-general` の6時間ごとの入口同期とは独立に、Leantime が要求する cron / schedule 実行を運用する。

## 採用方式の比較

| 方式 | 内容 | 利点 | 注意点 | 今回の評価 |
| --- | --- | --- | --- | --- |
| UI 参照 | 画面を観察し、情報階層・状態・密度を自前 UI に反映する | 結合せず、既存 P0 の SQLite / 将来の TypeScript 構成を保てる | 機能は自前実装になる | 最初に採る |
| 外部連携 | Leantime を独立運用し、GO 後に TODO / milestone を作成して画面遷移する | TODO、カレンダー、ガント、タイムシートを早く利用できる | 二重のID、同期方向、ユーザー・権限を定義する必要がある | 有力な P0 後続案 |
| fork / 改変 | Leantime コードを原本として機能・UIを直接変更する | 既存機能を深く改変できる | AGPLv3、PHP / MySQL 基盤、アップストリーム追随コストが重い | ライセンス判断前は採らない |

### 外部連携時の責務境界

```text
Slack / knowledge-vault / Web 入力
        -> pj-general: 入口保存・AI候補化・確認待ち・GO判断
        -> Leantime: GO済み TODO・subtask・milestone・calendar・gantt・timesheet
        <- pj-general: 状態 / 期限 / 担当の要約読取（必要になった時だけ）
```

- `pj-general` を入口、AI 分別、候補、判断履歴、knowledge-vault 参照の正本にする。
- Leantime を実行 TODO、マイルストーン、計画ビューの正本にする。
- 初期同期は一方向の `GO -> Leantime TODO 作成` に限定する。双方向同期は、更新競合と削除規則を決めてから進める。
- `candidate_id` と `leantime_ticket_id` の対応を `pj-general` 側に保存し、リンクで遷移できるようにする。

## 画面別に引用する対象

| pj-general 画面 | Leantime で見る画面・機能 | 借りる要素 | pj-general に残すもの |
| --- | --- | --- | --- |
| 書き入れ口 / 作成口 | Ideas、My Work の軽い入力・今日の見通し | アイデアから行動へ進める短い導線、過剰なフォームを避ける密度 | source、原文、AI 分類、GO 前の確認 |
| 横断ダッシュボード | My Work dashboard、Project dashboard | 今日・期限超過・今週・予定済みを一目で読むブロック、PJ進捗の置き方 | 入口別量、候補品質、判断ログ、横断 AI 状態 |
| TODO / タスクリスト | To Do table / list / kanban | 状態別グループ、行の情報密度、担当・優先度・期限の読み順、複数ビュー | 候補の真偽確認、AI提案、source provenance |
| タスク詳細 | TODO 詳細、subtask、コメント、依存 | タイトル、状態、担当、期日、依存、進捗を編集する順序 | GO前のAI要約・抜粋・不要判定 |
| ガント / タイムライン | Timeline / Gantt、milestone | milestone 単位の階層、期間バー、依存矢印、色の限定 | sourceから候補化した未確定情報 |
| カレンダー | Personal calendar / planned work | 予定化済みTODOを日・週・月で見る情報量 | Google Calendar 登録前のGO、外部カレンダーの正本 |
| 作業者用 / タスクサマリ | My Work、Timesheet / Timer | 今日やること、期限、時間記録の視認性 | Codex 起動支援、PJ固有の作業プロンプト |
| 管理画面 | users / project permissions / integrations | ロール・PJ単位の設定画面の整理 | source adapter、AI確定方針、タグマスタ、knowledge-vault対象 |

見た目を寄せる場合も、CSS や画面実装のコピーではなく、以下の設計原則を採る。

- タスク状態の色は少数に絞り、情報カードでなく行・列・見出しで密度を作る。
- My Work のように「今日」「期限超過」「今週」「後で」を分け、作業者が次の操作を選びやすくする。
- タスク詳細は右 drawer または専用ページに寄せ、一覧の横幅を保つ。
- ガントは milestone と TODO の関係が読める階層を優先し、装飾より日付と依存を優先する。

## Linux 配置の前提

- Leantime は PHP 8.2+、MySQL 8.0+ または MariaDB 10.6+、Web サーバーを要求する。
- 公式 Docker image と compose 構成が提供されている。`pj-general` の Node / SQLite P0 と同居させず、別 compose project と DB volume に分ける。
- reverse proxy 配下では専用の host または subdomain を使う。`pj-general` は Leantime URL を設定値として持ち、深いリンクを生成する。
- 定期入口同期は `pj-general` の systemd timer、Leantime 側の通知などの定期実行は Leantime の運用として分離する。

## 今回の判断待ち

`UJ-LEANTIME-01` を `docs/imp/user-judge.md` に置く。決定前には、OpenProject を外部ガント表示先とする実装には進まない。

## 一次情報

- Leantime GitHub README / license / screenshots: https://github.com/Leantime/leantime
- Leantime FAQ: https://docs.leantime.io/installation/frequently-asked-questions
- Leantime MCP: https://docs.leantime.io/installation/leantime-mcp
- Leantime API: https://docs.leantime.io/api/README
- Leantime configuration / cron: https://docs.leantime.io/installation/configuration
- Leantime plugins: https://docs.leantime.io/installation/using-plugins
