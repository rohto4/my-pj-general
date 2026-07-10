# P0 ガント補助表示仕様

作成日: 2026-07-09

## 目的

P0 で既に作成したガント表示を、TODO 主導線の補助表示として扱う最小範囲を定義する。

2026-07-10 の方針変更により、ガントは MVP の主目的ではない。個人の隙間時間で実行する TODO を主にし、ガントは期間や依存をまとめて確認したい時だけ使う。

## P0 表示項目

| 項目 | 意味 | P0 薄く実装 1 版 |
| --- | --- | --- |
| Task | タスクまたは予定候補の名前 | 表示する |
| Owner | 担当者 | 表示する |
| Progress | 進捗率 | 表示する |
| Timeline | 期間 | 横棒で表示し、横軸は週表示のメモリを打つ |
| Dependency | 依存元 | 補足テキストで表示する |

## データ接続

```text
AIRegistrationCandidate
-> GO
-> TODO / ScheduleCandidate
-> Gantt row
```

P0 本デモでは `gantt_tasks` テーブルの SQLite データを使って表示を確認する。

## 参照元

- 主参照: OpenProject Gantt chart
- 補助参照: Leantime task views

## P0 でやらないこと

- drag による期間編集。
- dependency line の直接編集。
- critical path。
- resource leveling。
- capacity management。
- Google Calendar との双方向同期。

## TODO 主導線への移行

- ダッシュボードの主遷移先は Vikunja の TODO 画面にする。
- Vikunja では同じ task から list / table / kanban / gantt を開けるため、ガント単独の外部遷移は作らない。
- P0 の簡易ガントは、Leantime 接続前の補助サマリとして残すか、TODOリンクに置換するかを実装時に決める。

## P0 完了後に検討すること

- 予定候補と Google Calendar 登録済み予定を同じ行に出すか。
- 外部協力者向けに見せる粒度を変えるか。
- 進捗率を手入力するか、状態から算出するか。

## 実装対応

- `apps/web/index.html` の `#gantt`
- `apps/web/app.js` の `ganttTasks`
- `apps/web/styles.css` の `.gantt-*`
