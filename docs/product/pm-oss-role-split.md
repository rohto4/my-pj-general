# PM 系 OSS の役割分担

## 目的

`pj-general` の入口・AI候補化と、GO後に日常的に実行する TODO を分離し、各 OSS の使いどころを固定する。

## 採用方針

- `pj-general` は Slack / knowledge-vault / Web 入力を受け、AI候補化、確認待ち、GO判断、判断履歴を正本として持つ。
- `Plane` は書き入れ口と AI 補助の情報設計を参照する。
- `Vikunja` は GO済みの実行TODOの体験と外部連携先の主候補にする。
- ガントは個人の隙間時間での実行を主目的にしない。Vikunja TODO の副次ビューとして、期間・依存を確認したい時だけ使う。
- `OpenProject` は横断計画・大規模権限・キャパ管理が要件化した場合の再評価候補に留める。

## 画面ごとの主参照先

| 画面・機能 | 主参照 | 借りるもの | pj-general が持つ正本 |
| --- | --- | --- | --- |
| 書き入れ口 / 作成口 | Plane、Leantime | 軽量入力、アイデアを行動に寄せる導線 | source、原文、AI分類 |
| 横断ダッシュボード | Plane、Leantime | 今日見るべきこと、期限・予定・実行状態の要約 | 入口別量、候補品質、判断ログ |
| TODO / タスクリスト | Leantime | list / table / kanban、担当・期限・優先度の読み順 | GO前の確認、source provenance |
| タスク詳細 | Leantime | subtask、コメント、依存、進捗、期日 | AI要約、抜粋、不要判定 |
| カレンダー | Leantime、Cal.com | 計画済みTODOの時間的な見通し | Google Calendar登録前のGO |
| ガント | Leantime | milestone、期間、依存をまとめて読む補助ビュー | 未確定候補の情報 |
| 人員計画・横断計画 | OpenProject | 将来の比較材料 | ロール、閲覧範囲、AI判断 |

## Leantime との責務境界

```text
Slack / knowledge-vault / Web入力
          -> pj-general: 入口保存・AI候補化・確認待ち・GO判断
          -> Leantime: GO済みTODO・subtask・milestone・calendar・gantt
          <- pj-general: 状態 / 期限 / 担当の要約読取（後続）
```

- 初期連携は `GO -> Vikunja task作成` の一方向に限定する。
- `candidate_id` と Vikunja task ID を `pj-general` 側で対応付ける。
- 双方向同期、削除同期、OpenProject への移行は別の設計・実装タスクに分離する。

## 参照資料

- `docs/candi-ref/leantime-adoption-and-ui-reference-2026-07.md`
- `docs/candi-ref/openproject-vs-leantime-integrated-comparison.md`
