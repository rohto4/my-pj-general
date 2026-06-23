# OSS 候補調査: 情報入口を含むプロジェクト管理ツール

## 調査日

- 2026-06-23

## 調査観点

- 雑な情報の入口があるか
- 入口からタスク化しやすいか
- チケット管理に強いか
- ガントやタイムラインを持つか
- 人・権限を扱えるか
- カレンダーや外部連携を伸ばしやすいか

## 結論サマリ

- 入口重視の第一候補は `Plane`
- 計画・ガント・権限重視の第一候補は `OpenProject`
- アイデア管理と個人起点の使いやすさを含む候補は `Leantime`
- 純粋なアジャイル課題管理の候補は `Taiga`
- 1本で「アイデア入口 + AI 自動タスク化 + Google Calendar + 精密キャパ管理」まで揃う OSS は、今回確認した範囲では見当たらない

## 1. Plane

### 合っている点

- `Pages` でアイデアやメモを保持し、行動項目へ変換しやすい
- `Intake` として in-app / forms / email の入口がある
- `Roles and permissions`、`custom roles`、`permissions matrix` がある
- `Dependencies in Timeline`、`estimates`、`time tracking`、`automations` がある
- `API`、`webhooks`、`MCP Server` がある
- `Plane AI` があり、AI 補助との相性が良い

### 弱い点

- 今回見た公式 docs では、Google Calendar を主軸にした標準機能は見えない
- ガントや人員キャパ管理は、OpenProject ほど前面には出ていない

### 向いている使い方

- 情報の入口を強くしたい
- アイデア -> タスク化 -> チケット運用を重視したい
- 将来 Codex / MCP とつなぎやすい土台を持ちたい

## 2. OpenProject

### 合っている点

- `Work packages` を中心に、task / feature / bug / phase / milestone などの型を持てる
- `Gantt charts` による計画とスケジューリングが強い
- `Team Planner` で assignee 単位の週次・隔週カレンダー配置ができる
- `Custom fields`、`workflows`、`users and permissions`、`API and webhooks` がある
- Community Edition が広く、self-host 前提の管理基盤として強い

### 弱い点

- 情報入口は Plane や Leantime ほど前面に出ていない
- アイデアカード起点の運用は、work package 設計で寄せる必要がある
- チーム負荷の見える化はあるが、精密なキャパ自動最適化は別設計になりそう

### 向いている使い方

- Jira 的な計画管理、権限、進捗、ガントを重視したい
- まず堅い PM / issue 管理の骨格を持ちたい

## 3. Leantime

### 合っている点

- `Ideas`、`Docs`、`To Dos`、`Milestones` を同じプロジェクト空間で扱える
- task view は `kanban`、`table`、`list`、`calendar` がある
- `gantt`、`dependencies`、`timesheets`、`multiple user roles and per project permissions` がある
- GitHub README と公式サイトの両方で、アイデア管理とプロジェクト管理の近さが確認できる
- 非 PM 向け、個人起点でも入りやすい

### 弱い点

- エンタープライズ寄りの堅い課題管理や大規模権限設計は OpenProject より弱く見える
- AI や外部連携の広さは Plane ほど前面に出ていない

### 向いている使い方

- アイデア入口とタスク管理を近く置きたい
- 個人利用からチーム利用へ広げたい
- 思考整理と実行管理を一体で扱いたい

## 4. Taiga

### 合っている点

- Kanban / Scrum / Issues が強い
- `roles & permissions`、`custom tags and fields`、`REST API`、`webhooks`、各種 integrations がある
- issue を user story に昇格できるなど、アジャイル課題管理の文脈は強い

### 弱い点

- 情報入口やアイデア蓄積の強さは今回の候補中では弱い
- ガントや個人起点の思いつき蓄積には主軸が寄っていない

### 向いている使い方

- 入口よりもアジャイルなチケット管理を優先したい
- Scrum / Kanban ベースの開発運用を強くしたい

## 現時点の推奨

### 第1群

- `Plane`
- `OpenProject`

この2つが、今回の「情報入口」と「計画管理」の両極として最も比較価値が高い。

### 第2群

- `Leantime`

アイデア入口を重視するなら強い候補。個人起点の使いやすさもあるため、比較対象に残す価値が高い。

### 第3群

- `Taiga`

チケット管理専用寄りの比較対象としては有効。ただし今回の主要求との一致度は上位 3 件より下がる。

## 現時点の設計示唆

- 「雑な入口」は Plane または Leantime の発想が近い
- 「Jira 的な複数人・複数タスク管理」は OpenProject または Taiga の発想が近い
- したがって、最終的には
  - 1本の OSS を深く拡張する
  - 入口寄り OSS と計画寄り OSS の思想を比較して内製する
の二択に近づく可能性が高い

- Google Calendar 連携は、今回確認した範囲では標準中核機能としては見えず、`API / webhooks / custom integrations` 前提で考えるのが自然
- 人員キャパ管理も、単なる可視化を超えるなら内製ロジックが必要になりやすい

## 現時点の設計判断メモ

- 情報入口は自前実装を前提にした方がよい
- 完成された OSS を丸ごと採用するより、ガントチャートやスケジュール表示のような視覚表現部分だけ借りる方が要件適合しやすい
- このため、今後の OSS 調査は「プロダクト候補」だけでなく「描画ライブラリ候補」も別軸で行うべき
- 横断ダッシュボードの情報設計は、既存 PJ 管理 OSS の構造を参考にする方針がよい
- 実績参照は初期 UI よりも、履歴データをどこまで残すかを先に定義すべき

## 一次情報

- OpenProject: https://www.openproject.org/
- OpenProject work packages: https://www.openproject.org/docs/user-guide/work-packages/
- OpenProject team planner: https://www.openproject.org/docs/user-guide/team-planner/
- OpenProject GitHub: https://github.com/opf/openproject
- Plane: https://plane.so/
- Plane docs: https://docs.plane.so/
- Plane GitHub: https://github.com/makeplane/plane
- Leantime: https://leantime.io/
- Leantime GitHub: https://github.com/Leantime/leantime
- Taiga: https://taiga.io/
- Taiga docs: https://docs.taiga.io/
