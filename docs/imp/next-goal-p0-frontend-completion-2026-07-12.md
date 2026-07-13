# 次の目標: P0フロント受入完了

P1実機運用仕上げへ進む前に、Hub / Vikunjaの画面操作を実装実体と一致させる。

## 対象

1. 表示される全button / link / formの操作監査
2. Hub候補・確認待ち・判断ログ・GOのフロント受入
3. Tasks概要・直近task・ガントの読み取り責務と導線
4. Vikunja主要画面のguide、empty state、主操作
5. 最新DB/APIフィールドと画面表示・編集の同期
6. 1280px / WQHD / 4K縦3分割相当の実画面操作受入

## 完了条件

- 主要操作が実画面で成功し、保存後の一覧・件数・状態・リンクが更新される。
- 機能しないボタンが残らず、読み取り専用の箇所は理由と編集先が明示される。
- HubとVikunjaの操作責務が混同されない。
- 最新データ構造がフロントへ漏れなく反映される。
- UI操作受入、回帰、build、設計書の証跡を残す。

## 現在のユーザー判断待ち（RV01〜RV05）

実装済み画面の完成度を別の残タスクとして切り出し、`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`の最上部から実行できるようにする。各項目は黄色枠付き画像を開き、許容なら完了、改善が必要または判断不能なら未達とコメントする。実データ変更は行わない。

- RV01 Dashboard: 処理状況、30日カレンダー、未日程/最近のタスク/ビューの縦順と密度
- RV02 Gantt: guide、日付範囲・時間軸、下部空白、初期導線
- RV03 Kanban: 4列の同時認識、列幅、内部スクロール、下部空白
- RV04 Task detail: タイトル/メタ情報、説明、コメント、操作面の読み順
- RV05 証跡: before/afterの画面高不一致と再撮影要否

黄色枠画像は `tmp/ui-review/p0-review-2026-07-12/README.md` に一覧化している。Thread Line画像調整とR03のALLOKは今回のレビュー対象外とする。

## 2026-07-12 ユーザー再受入後の優先順

1. RV01 Dashboardの不要ブロック削除・PJ名表記・処理状況左寄せ・日付未定タスクの完了除外
2. RV02 Ganttの既定期間、日付変更確認/取消、完了バーのグレー化
3. RV03 Kanbanのguide削除・無制限縦高・内部スクロールバー削除
4. RV04 Task detailのパンくず順、狭幅右操作群、説明/コメント文字サイズ
5. RV05を1438x715同一条件で再撮影し、全比較証跡を揃える
6. U01初回Gantt再現、U02 AI要約/タグ生成改善、U03判断ログのAPI/DB/bootstrap照合
7. R06 Tasks本文のHub由来オレンジをTasks青・淡青へ統一し、再配信後にprimary/link/focus/選択行/left rail/button/card/task/dashboard/calendarの残存なしを受入する
8. R07 Tasksのプロジェクト・ラベル・チームを`マスタ管理`の一画面へ統合し、個別メニューの廃止、登録・確認・既存編集導線、4K縦3分割相当の横崩れなしを受入する

Tasks左レールは、Hubのアイコン輪郭・記号・24px枠・行高を共有し、Hubのみ銅オレンジ、Tasksのみ `--threadline-tasks-accent` の青で表示する。R05でLinux反映とAPI 200・実データ維持は確認済みだが、Tasks本文にHub由来のオレンジが残るため、R06の青・淡青テーマ再配信と実機確認を先に行う。

## 保留するもの

- P1のsystemd、backup timer、custom image rollback、PoC最終判定はこの目標の後に再開する。
- HubでVikunja taskを直接編集するかどうかは、現行の「Vikunjaを実行TODOの正本とする」境界を確認してから決める。
