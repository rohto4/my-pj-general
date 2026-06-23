# OpenProject と Leantime の一体比較

## 比較目的

- `ガント + TODO / タスク` が一体化している OSS を優先候補として比較する
- `入口自前 + PM 機能借用 + ガント統合` の構成で、どちらが主参照先に向くかを判断する

## 前提

- 入口 UI は自前実装
- `Plane` は入口周辺の情報設計や AI 補助の主参照
- ここでは `ガント + TODO / タスク` の一体性だけを主に見る

## 一体性の観点

### 1. 中心オブジェクト

#### OpenProject

- `Work packages` が中心
- そこから `Gantt charts`, `Agile boards`, `Calendar`, `Team planner` へ展開する

評価:

- 一体性が強い
- タスクと計画ビューが同じ土台でつながっている

ソース:

- https://www.openproject.org/docs/user-guide/work-packages/
- https://www.openproject.org/docs/user-guide/gantt-chart/

#### Leantime

- README 上で `task management via kanban boards, gantt, table, list and calendar views`
- `Idea Boards` もあり、アイデアから TODO への距離が近い

評価:

- 一体性は高い
- 特に `ideas -> goals -> todos -> gantt` の流れが魅力

ソース:

- https://github.com/Leantime/leantime

## 2. ガントとの結びつき

### OpenProject

- ガントは `work packages` の延長
- 依存関係、日付、期間、階層が自然につながる
- 横断ダッシュボードや権限とも接続しやすい
- 公式の `Team planner` は assignee 列つきの計画ビューとして整理されている

評価:

- `計画系ガント` として強い
- ただし人員計画まわりは Community Edition でそのまま再利用できる範囲と分けて考える必要がある

### Leantime

- ガントを task management view の1つとして持つ
- 個人や小規模チームが扱いやすそうな軽さがある

評価:

- `実行寄りガント` として良い

## 3. TODO / タスクリストの見え方

### OpenProject

- 重厚で業務的
- work package table, board, backlog, planner の連動が強い

評価:

- 横断管理向き
- ただし入口に近い軽快さは弱い

### Leantime

- list, table, kanban, calendar, gantt が近い
- ideas から task へ育てる流れが見えやすい

評価:

- TODO の使い心地は魅力がある
- デザイン借用候補として価値が高い

## 4. 今回要件との相性

### OpenProject が強い点

- Web で見られる
- 権限、横断管理、ガント、planner が強い
- 外部協力者やロール前提の構造に寄せやすい
- `work packages -> gantt -> team planning` のつながりが明快

### OpenProject が弱い点

- 入口や雑メモの軽さは弱い
- UI の印象はやや重い
- `Team planner` は公式ドキュメント上で Enterprise add-on 扱い

### Leantime が強い点

- ideas と TODO と gantt の距離が近い
- 非 PM にも扱いやすい設計思想
- あなたの `書き入れ口 / 作成口` に近い

### Leantime が弱い点

- 権限や大規模横断管理は OpenProject より弱く見える
- 利用者数やレビュー量の厚みは OpenProject より弱い

## 現時点の仮結論

### 主参照先として強い

- `OpenProject`

理由:

- `ガント + TODO` の一体性に加えて、横断管理と権限までつながるため
- ただし人員キャパ管理の実装参照では、OpenProject をそのまま採るというより構造参照として扱う方が安全

### デザイン / 体験の補助参照として強い

- `Leantime`

理由:

- `ideas -> todos -> gantt` の流れが、今回の入口思想に近い
- TODO / task list のデザイン借用候補として魅力がある

## 次に見るべき観点

1. OpenProject の work package table / gantt / planner のつながり
2. Leantime の ideas / todos / gantt / dashboard のつながり
3. TODO リスト UI をどちらから濃く借りるか
4. ガントは OpenProject 主体にし、TODO は Leantime 参考に寄せるか
5. OpenProject の Enterprise add-on 領域を、どこまで要件参考に含めるか
