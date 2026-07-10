# TODO UI 候補

調査日: 2026-07-10

## 目的

`pj-general` の確認待ちキューで GO した後に遷移する、日常的に開きたくなる TODO 画面の候補を比較する。

評価は機能の網羅性よりも、個人の隙間時間で「次の一件をすぐ実行できる」見た目、情報密度、自己ホスト、`GO -> TODO` 連携のしやすさを優先する。

## まず見る候補

| 候補 | 見た目の方向 | TODO 表示 | 今回の位置付け | リンク |
| --- | --- | --- | --- | --- |
| Leantime | やわらかく、非PMユーザーが使いやすい。My Work と PJ画面がある | list / table / kanban / calendar / gantt、subtask、dependency、goal、timesheet | UI・機能比較の参照候補 | https://leantime.io/ |
| Vikunja | 現代的で軽い。タスク中心で余白と色が控えめ | list / table / kanban / gantt、Quick Add、フィルタ、詳細pane | **実運用の第一候補**。API / Webhook / backend pluginを検証する | https://vikunja.io/ |
| Kan | Linear / modern SaaS に近い、濃いめのモダンKanban | board、label、filter、comment、activity、template | **UI参照候補**。board中心の気分を上げる画面 | https://kan.bn/ |
| Plane | Linear寄りで高密度。Intakeとトリアージの見た目が強い | work item、triage、project、cycle、module、docs | **UI / 入口参照候補**。本PJの確認待ちキューとの親和性が高い | https://plane.so/ |
| Super Productivity | 集中作業向けで、時間箱・タイマーが主役 | task、subtask、project、tag、timeboxing、time tracking | **個人作業体験の参照候補**。サーバー側の実行基盤にはしない | https://super-productivity.com/ |
| Wekan | Trello互換の素直なKanban | board、list、card、期限、custom field | **軽量カンバン比較用**。標準ガントなしのため本命ではない | https://wekan.github.io/ |

## 優先して見る画面

### Leantime

1. My Work dashboard: 今日、期限超過、今週、予定済みをどう置くか。
2. To Do table / list: タイトル、担当、期限、状態を読む順序。
3. Task detail: subtask、依存、コメント、期日の編集密度。
4. Calendar / Gantt: TODOの副次ビューとして日付・依存を読む方法。

### Vikunja

1. List: Quick Add とドラッグ並べ替え。
2. Table: 多属性を比較する時の列設計。
3. Task detail: 右側フィールドと本文の情報階層。
4. Kanban: カードと状態色の最小限の使い方。

### Kan / Plane

1. board / work item list: 背景、列、カード、タグの配色。
2. detail pane: 一覧を崩さず詳細を編集する構成。
3. intake: 受信情報をそのまま候補にし、人が判断する画面密度。

## 現時点の推奨

- 実運用の本線は Vikunja。Linux上に独立自己ホストし、`pj-general` の GO から一方向に task を作成する。
- 比較試用の優先順は `Vikunja -> Leantime -> Kan -> Plane`。
- Vikunjaは、まずAPI / Webhook / backend pluginを検証する。TODO画面を変える必要が明確になった場合だけforkを判断する。
- `Kan` と `Plane` は画面表現を借りる候補。実行基盤として選ぶ前に、API、継続性、ライセンスを別途確認する。

## 一次情報

- Leantime: https://github.com/Leantime/leantime
- Vikunja: https://vikunja.io/ / https://vikunja.io/help/views/
- Kan: https://github.com/kanbn/kan
- Plane: https://github.com/makeplane/plane
- Super Productivity: https://github.com/super-productivity/super-productivity
- Wekan: https://github.com/wekan/wekan
