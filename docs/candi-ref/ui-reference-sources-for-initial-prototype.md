# 初期プロトタイプ UI 参考資料

## 目的

この文書は、`pj-general` の初期プロトタイプで各画面の見た目・情報設計・操作感を作るときに参照する資料を、画面別に整理する。

現時点では、特定 OSS を丸ごと採用するのではなく、`Next.js + shadcn/ui + Tailwind CSS` で自前実装し、画面ごとに高品質な既存 UI / OSS の構造や体験を参照する方針を第一候補にする。

## 既存調査から確認できた前提

- `tech-stack.md` では、Web は `Next.js App Router`、UI は `shadcn/ui`、Style は `Tailwind CSS`、Icon は `lucide-react` が第一候補。
- `docs/arch/recommended-oss-and-stack-composition.md` では、入口は自前、計画系ビューは OSS の思想と一部実装を借りる方針。
- `docs/product/pm-oss-role-split.md` では、入口は `Plane`、ガントと横断計画は `OpenProject`、TODO とアイデア昇格は `Leantime` を主参照にする方針。
- `docs/candi-ref/oss-candidates-intake-pm.md` では、情報入口の第一候補を `Plane`、計画・ガント・権限の第一候補を `OpenProject`、個人起点の使いやすさを含む候補を `Leantime` と整理済み。
- `docs/candi-ref/shadcn-and-gantt-constraints.md` では、入口 UI は自前実装でよく、UI 基盤は `shadcn/ui` が自然と整理済み。

## 画面別の参照資料表

| 参考資料 | 対象画面 | 概要 | 初期プロトタイプで借りる観点 | リンク |
| --- | --- | --- | --- | --- |
| shadcn/ui | 全画面の UI 部品基盤 | Tailwind CSS と Radix UI を前提に、コードとして取り込んで編集できる UI 部品群。既存調査でも入口 UI 基盤として自然と判断済み。 | Button、Card、Dialog、Command、Form、Table、Tabs、Select、Badge、Sheet、Tooltip などの部品。デザインシステムを外部依存に閉じず、自前コードとして育てる。 | https://ui.shadcn.com/ |
| shadcn/ui Blocks | 横断ダッシュボード、作業者用 / タスクサマリ、管理画面 | ダッシュボード、サイドバー、認証、フォーム、リストなどの組み合わせ例。 | 初期実装のレイアウト密度、サイドナビ、ヘッダー、カードではなく業務パネルとしての情報配置。 | https://ui.shadcn.com/blocks |
| shadcn/ui Tasks example | TODO / タスクリスト、確認待ちキュー | タスク一覧の table / filter / view options の実装例。 | AI 分別後の候補一覧、TODO 一覧、確認待ちキューのテーブル操作、フィルタ、ステータス表示。 | https://ui.shadcn.com/examples/tasks |
| Plane | 書き入れ口 / 作成口、確認待ちキュー、作業者用 / タスクサマリ | モダンな PM / knowledge management ツール。Intake、AI triage、Slack から work item 作成など、入口から作業化への導線が近い。 | 「雑な入力 -> 整理候補 -> work item」への画面導線、モダンで軽いプロジェクト管理の密度、AI 補助前提の情報設計。 | https://plane.so/ |
| Plane Docs | 書き入れ口 / 作成口、入口設定、確認待ちキュー | Plane の Intake、Issue / Work item、Timeline、Roles and permissions などの仕様確認先。 | 入口イベント、タスク候補、権限、タイムラインを分けて見せるときの情報単位。 | https://docs.plane.so/ |
| OpenProject | 横断ダッシュボード、ガント、管理画面、権限まわり | Work packages を中心に、ガント、ボード、カレンダー、Team planner、権限を接続する PM ツール。 | 横断計画の中心オブジェクトをどう見せるか、複数人・複数 PJ・権限あり表示の構造。 | https://www.openproject.org/ |
| OpenProject Work Packages | 横断ダッシュボード、TODO / タスクリスト、ガント | OpenProject の中心オブジェクトで、タスク、機能、バグ、マイルストーンなどを扱う単位。 | `IdeaCard -> Todo -> ScheduleCandidate` を画面上で一貫した業務オブジェクトとして扱う発想。 | https://www.openproject.org/docs/user-guide/work-packages/ |
| OpenProject Gantt chart | ガント、横断ダッシュボード | Work packages とガントを接続する公式ドキュメント。階層、期間、依存関係、進捗の表示に強い。 | P0 ガントを「タスク一覧の別表示」として扱う構造。初期は表示優先で、編集体験は後続評価に回す。 | https://www.openproject.org/docs/user-guide/gantt-chart/ |
| OpenProject Team Planner | 人員計画、外部協力者表示、作業者用 / タスクサマリ | assignee ごとの週次 / 隔週計画ビュー。Enterprise add-on 領域なので、実装流用ではなく構造参照。 | 人別の予定・作業割当の見せ方。MVP ではキャパ管理を入れないが、将来の見せ方の基準にする。 | https://www.openproject.org/docs/user-guide/team-planner/ |
| Leantime | 書き入れ口 / 作成口、TODO / タスクリスト、ガント補助 | Ideas、Docs、To Dos、Milestones、Gantt などを軽くつなぐ、個人・小規模チーム寄りの PM ツール。 | `ideas -> todos -> gantt` の近さ、非 PM ユーザーでも扱いやすい軽さ、個人起点からチームへ広げる画面感。 | https://leantime.io/ |
| Leantime GitHub | TODO / タスクリスト、アイデア昇格、ガント補助 | README で kanban / gantt / table / list / calendar view、Idea Boards、dependencies などを確認できる。 | タスクビューの切り替え、アイデアボードから TODO へ育てる操作、軽量ガントの補助参照。 | https://github.com/Leantime/leantime |
| Cal.com | Google Calendar 連携導線、スケジュール登録画面 | 日程調整・予約・可用時間管理に強い OSS / サービス。 | Google Calendar へ登録する前の確認、空き時間・候補時間・参加者予定を扱う画面の参考。 | https://cal.com/ |
| FullCalendar | スケジュール表示、履歴 / 実績参照 | JavaScript のイベントカレンダー UI ライブラリ。React でも利用できる。 | P0 で Calendar 風の表示が必要になった場合の描画候補。Google Calendar 連携の確認画面にも使える可能性。 | https://fullcalendar.io/ |
| NocoBase | 管理画面、タグマスタ、入口設定 | ノーコード / ローコード寄りの内部ツール・管理画面構築基盤。 | 分類タグマスタ、入口ごとの設定、テンプレート管理など、管理系画面の密度と構成。 | https://www.nocobase.com/ |
| Linear | 作業者用 / タスクサマリ、TODO / タスクリスト | 高速で密度の高い issue tracking / project planning 体験。OSS ではないため実装流用ではなく UI 体験参照に留める。 | タスク詳細、ステータス、ショートカット前提の軽快な作業画面。ただし丸写しせず、操作密度の参考に限定する。 | https://linear.app/ |
| Notion Databases | 書き入れ口 / 作成口、履歴 / 実績参照 | データベースビュー、フィルタ、プロパティ、ページ化された情報管理の代表的 UX。 | アイデアカード、判断記録、履歴参照を「構造化されたノート」として扱うときの見せ方。 | https://www.notion.com/help/category/databases |

## 初期プロトタイプの採用方針

### 1. UI / FW

- 第一候補は既存方針どおり `Next.js App Router + Tailwind CSS + shadcn/ui + lucide-react`。
- 初期は `apps/web` に 1 つの Web アプリとして作り、管理画面は route group / navigation 上の区分に留める。
- `shadcn/ui` は npm package として黒箱利用するより、生成されたコードを `packages/ui` または `apps/web` 側で管理する前提にする。

### 2. 書き入れ口 / 作成口

- 主参照は `Plane`、補助参照は `Leantime`。
- 画面は「大きな入力欄 + 分類候補 + 関連候補 + GO / 保留 / 修正」の流れを優先する。
- 初期は Slack / Misskey / knowledge-vault の実連携を作らず、同じ `IntakeEvent` 型の mock data で確認する。

### 3. 確認待ちキュー

- 主参照は `shadcn/ui Tasks example` と `Plane Intake / AI triage`。
- テーブル、フィルタ、ステータス、AI 提案内容、GO / 保留 / 修正の操作を最小単位にする。
- P0 薄く実装 1 版では全件を確認待ちにし、人の GO を挟む。P0 全体完了時点で部分自動確定へ進める。

### 4. 横断ダッシュボード

- 主参照は `OpenProject`、補助参照は `Plane` と `shadcn/ui Blocks`。
- 表示対象は、整理候補、TODO、予定化候補、ガント、最近の判断記録を横断する。
- 個人利用ベースでも、外部協力者に見せる範囲を後で切れるように、画面上の情報単位を分ける。

### 5. TODO / タスクリスト

- 主参照は `Leantime`、補助参照は `OpenProject Work Packages` と `shadcn/ui Tasks example`。
- list / table / kanban / calendar / gantt の切り替え思想は借りるが、P0 では list/table とガント表示を優先する。

### 6. ガント

- 主参照は `OpenProject Gantt chart`、補助参照は `Leantime`。
- 初期実装では編集可能な本格ガントライブラリ導入を急がず、タスク・期間・依存・担当・進捗の表示を mock data で確認する。
- ドラッグ編集、依存線編集、クリティカルパス、リソース平準化は P0 以後の評価対象にする。

### 7. Google Calendar 連携導線

- 主参照は `Cal.com`、描画候補は `FullCalendar`。
- P0 はユーザー GO で登録する前提なので、まず「予定候補を確認し、Calendar 登録へ進む」画面に集中する。

### 8. 管理画面

- 主参照は `NocoBase` と `OpenProject` の管理系構造、UI 部品は `shadcn/ui`。
- 分類タグマスタ、Codex プロンプトテンプレート、入口設定、ロール表示範囲を扱う。
- 初期は管理対象を増やしすぎず、P0 の画面確認に必要な項目に絞る。

## 今回時点の不足

- `docs/spec/screen-structure-p0.md` は未作成。
- `docs/spec/gantt-mvp-flow.md` は未作成。
- したがって、この文書は次に作る画面構成仕様とガント MVP 仕様の入力資料として扱う。

## 次に仕様へ落とすこと

1. `docs/spec/screen-structure-p0.md` を作成し、4 窓口と P0 画面の構成を固定する。
2. `docs/spec/gantt-mvp-flow.md` を作成し、P0 ガントの表示対象、操作対象、未対応範囲を固定する。
3. 初期実装では `apps/web` に mock data ベースの画面を作り、Codex とユーザーで画面を見ながら拡張する。
