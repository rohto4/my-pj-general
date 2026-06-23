# OSS 候補調査: ガント / プロジェクト管理 / スケジュール管理

## 目的

優先度順に、次の色が強い OSS を整理する。

1. ガントチャート
2. プロジェクト管理
3. スケジュール管理

## 1. ガントチャート色が強い候補

### OpenProject

- 公式に `Project planning and scheduling` と `Gantt charts` を前面に出している
- `Team Planner` もあり、ガントと人員カレンダーが近い
- Web ベースで、複数人運用や権限まで含めて見やすい
- OSS 本体として公開されており、今回の `Web で見られる` 条件に合う

向き:

- Web アプリの中でガントをどう位置づけるかの参考
- ガントとタスク管理を一体で見せる構造を参考にしたい
- フォークやデザイン変更の起点にしやすい

### Redmine

- Web ベース
- Gantt と Calendar を標準で持つ
- 実利用レビュー数が多く、古典的だが比較基準として有効

向き:

- Web 上での基本的な Gantt / Calendar の載せ方を参考にしたい
- シンプルな情報密度の基準線を見たい

注意:

- デザイン刷新前提で見る方が自然

### ProjectLibre

- `Advanced Gantt Charts`、`Work Breakdown Structures`、`resource management` を掲げる
- Microsoft Project 代替色が強い
- Desktop の open source 版があり、ガント中心の PM 文脈が強い

向き:

- ガントと WBS の組み合わせ
- PM ツール寄りの情報設計

注意:

- Desktop 主体で、今回の Web 条件には合いにくい
- Cloud 側は商用色が強く、参照範囲を切って使う必要がある

### GanttProject

- 公式に `Gantt chart for small and medium businesses` を掲げている
- `build a Gantt chart, assign resources and calculate project costs` とあり、ガント表示そのものが中心
- `Local-first, works offline` のデスクトップ型

向き:

- ガント画面の情報密度や UI の割り切り方を参考にしたい
- Web アプリ全体ではなく、ガント表現の思想を借りたい

注意:

- 今回追加された `Web で見られる` 条件には合いにくい
- 参照対象としては残るが、本線候補からは一段落ちる

## 2. プロジェクト管理色が強い候補

### OpenProject

- `Work packages`、`Gantt charts`、`Boards`、`Backlogs`、`API` を持つ
- `classic, agile or hybrid project management` を公式に掲げる
- `Team Planner` で担当者単位の計画も見られる

向き:

- 全体ダッシュボード
- 複数人・複数タスク管理
- 権限あり運用

### Plane

- `Project management and knowledge management for teams and agents`
- `Projects, docs, and AI-powered workflows`
- docs 上で `Roles and permissions`、`Intake`、`Timeline dependencies`、`API`、`Webhooks`、`MCP Server` を確認できる

向き:

- 入口から実行までのつながり
- AI 補完とプロジェクト管理の接続
- 現代的な情報設計

### Leantime

- `Projects are where you "Think" and "Make"` として `To Dos`、`Milestones`、`Ideas`、`Docs`、`Reports`、`Timesheets` を一体で持つ
- `gantt chart`、`dependencies`、AI 補助を持つ

向き:

- アイデア入口とプロジェクト管理の距離が近い構造
- 個人起点からチーム管理へ広げる発想

### Taiga

- `Kanban`、`Scrum`、`Issues`、`roles & permissions`、`REST API`、`webhooks`
- アジャイル課題管理色が強い

向き:

- チケット管理やアジャイル運用の比較対象

注意:

- 今回の「雑な入口」や「スケジュール」より、issue 管理寄り

## 3. スケジュール管理色が強い候補

### Cal.com

- `Set your availability`
- `calendar syncing`
- `round-robin scheduling`
- `shared availability`
- GitHub 上で OSS として公開され、スター数も大きい

向き:

- 予定登録
- 空き時間管理
- チームスケジューリング

注意:

- プロジェクト管理より、予約・日程調整寄り

### Nextcloud Groupware

- `Calendar, Contacts, Mail`
- `Meeting time proposals`
- `track availability`
- `Appointment scheduling, resource booking`
- `Gantt charts, card dependencies in Nextcloud Deck`

向き:

- カレンダーとチームスケジュール
- 会議調整や空き時間確認
- グループウェア寄りの scheduling

注意:

- PM ツールそのものではなく、グループウェア寄り

### OpenProject

- `Team Planner`
- assignee ごとの weekly / bi-weekly calendar planning
- スケジュール可視化は強い

向き:

- タスク由来のスケジュール管理
- プロジェクト計画と人員計画の接続

注意:

- 予約・調整専用ツールではない

## 現時点の優先結論

### ガント優先でまず見る

1. `OpenProject`
2. `Redmine`
3. `ProjectLibre`
4. `GanttProject`

### プロジェクト管理で見る

1. `OpenProject`
2. `Plane`
3. `Leantime`
4. `Taiga`
5. `Redmine`
6. `Tuleap`

### スケジュール管理で見る

1. `Cal.com`
2. `Nextcloud Groupware`
3. `OpenProject`
4. `Redmine`

## デモ / 試用導線メモ

### すぐ見やすい

- `OpenProject`: 公式サイトから `Start free trial`
- `Plane`: 公式サイトから `Get started free`
- `Leantime`: 公式サイトから `Sign Up`
- `Taiga`: 公式サイトから `Get Taiga`
- `Cal.com`: 公式サイトから `Get started` と `Book a demo`

### ダウンロード型

- `GanttProject`: 公式サイトから `Download`
- `ProjectLibre`: 公式サイトから `Download Desktop`

### グループウェア型

- `Nextcloud Groupware`: 公式サイトから `Try Nextcloud Groupware`

## デモを見る順番の提案

1. `OpenProject`
2. `Plane`
3. `Cal.com`
4. `GanttProject`
5. `ProjectLibre`

理由:

- まず Web 全体の横断ダッシュボードとガントのバランスを見る
- 次に入口や現代的な情報設計を見る
- その次に scheduling 専用の強さを見る
- 最後にガント専用寄りの desktop ツールで表示思想だけ吸う

## 設計示唆

- `Web で見られてフォークしやすい` という条件を入れると、ガントの主参照先は `OpenProject`、次点で `Redmine`
- `ProjectLibre` と `GanttProject` はガント表現の参考にはなるが、desktop 主体なので本線からは一段下がる
- 全体ダッシュボードや PJ 横断管理の主参照先は `OpenProject`
- 書き入れ口や AI 補完の思想は `Plane` と `Leantime`
- スケジュール管理は `Cal.com` や `Nextcloud Groupware` の発想を別軸で吸うのがよい
- `Tuleap` は大規模運用・権限・トレーサビリティ寄りの比較対象として別格で残す

## 一次情報

- OpenProject: https://www.openproject.org/
- OpenProject Team Planner: https://www.openproject.org/docs/user-guide/team-planner/
- OpenProject Work Packages: https://www.openproject.org/docs/user-guide/work-packages/
- Plane: https://plane.so/
- Plane docs: https://docs.plane.so/
- Leantime: https://leantime.io/
- Taiga: https://taiga.io/
- Taiga docs: https://docs.taiga.io/
- GanttProject: https://www.ganttproject.biz/
- ProjectLibre: https://projectlibre.com/
- Cal.com: https://cal.com/
- Cal.com GitHub: https://github.com/calcom/cal.diy
- Nextcloud Groupware: https://nextcloud.com/groupware/
