# Handoff 2026-06-23

## 今回の到達点

- このPJは `やりたいこと抽出フェイズ` として進行
- 要件は `実装時期` より `網羅性` を優先して整理
- UI は 4 窓口に分ける方針を確定
- `入口は自前実装` の方針を確定
- 入口UI基盤候補として `shadcn/ui` を採用候補に追加
- `Slack` と `knowledge-vault` を定期回収する外部入口要件を追加
- `Codex プロジェクト開始支援` を要件に追加
- OSS 比較は複数 md に整理済み
- 現時点の温度感として `Plane` がかなり強い候補
- ガントは別 OSS / 別レイヤーで統合する方向に寄っている
- `Redmine` は古さを理由に候補から外す判断
- タスクリスト / TODO リストもデザインが重要なので、OSS の部分取り込み候補に含める

## 現時点の主要判断

### プロダクト方針

- 入口は OSS プロダクト流用ではなく、自前実装
- 差別化要因は `入口 -> AI分別 -> タスク化 / 予定化 / 検討事項化` の一気通貫
- タスクリスト、TODO リスト、ガント、スケジュール表示、負荷可視化のような高コスト UI は OSS 借用候補

### UI 方針

- 1. 横断ダッシュボード
- 2. 上位管理者用の管理画面
- 3. 書き入れ口 / 作成口
- 4. 実績・履歴参照

### 入口要件

- 手入力
- Slack 回収
- knowledge-vault 回収
- 各 1 時間ごとに自分の投稿を回収
- AI が自動分別
- 分類先は:
  - タスク
  - スケジュール
  - 検討内容
  - 気になっている事

### Codex 支援要件

- 初期プロンプト生成
- フォルダ構成ひな型選定
- テンプレート流用元の提示
- AGENTS / PROJECT / docs 初期化支援

## OSS の現時点整理

### 主参照候補

- `Plane`
  - modern OSS
  - AI capabilities
  - Pages
  - 情報設計と体験の主参照

- `OpenProject`
  - ガント
  - 横断管理
  - 権限
  - Team Planner

- `Taiga`
  - アジャイル課題管理寄り
  - ガント候補の補助比較

### 補助候補

- `Cal.com`
  - スケジュール管理思想

- `Tuleap`
  - 権限 / traceability / ALM

- `ProjectLibre`
  - ガント専用寄り比較

- `GanttProject`
  - ガント表示思想の参考

### 追加候補

- `Taiga`
- `Odoo`
- `ERPNext`
- `WeKan`

## 重要な現時点の温度感

- `Plane` はかなり熱い
- ただし `入口そのもの` を Plane で置き換えるのではなく、`情報設計 / AI補助 / modern UI思想` の参照元として使う想定
- ガントは `Plane 以外` を統合する方向が自然
- 現時点の本線仮説は `入口自前 + Plane + 別ガント統合`

## 次セッションの最優先テーマ

- `Plane を何の参照元として使うか` を固定する
- `ガントチャートを何で統合するか` を絞る

## 次にやること

1. `Plane` を参照する対象を明文化する
2. `OpenProject` と `Taiga` のガント画面を比較する
3. `Web で見られて OSS フォークしやすい` ガント候補をさらに絞る
4. `自前入口 + 別ガント統合` の構成仮説を docs に落とす

## 未決事項

- Slack / knowledge-vault 回収後の AI 分別を自動確定するか、確認キューを挟むか
- Google Calendar 連携をどこまで自動化するか
- ガントの表示だけ借りるのか、編集操作まで借りるのか
- 実績データの最小保持項目

## 次セッションで先に読むファイル

1. `docs/product/idea-to-plan-discovery.md`
2. `docs/candi-ref/adoption-and-recency-reselection.md`
3. `docs/candi-ref/oss-candidates-by-visual-priority.md`
4. `docs/candi-ref/shadcn-and-gantt-constraints.md`
5. `docs/candi-ref/demo-comparison-checklist.md`
6. `docs/imp/user-judge.md`

## 今回作成・更新した主なファイル

- `docs/product/idea-to-plan-discovery.md`
- `docs/candi-ref/oss-candidates-intake-pm.md`
- `docs/candi-ref/oss-candidates-by-visual-priority.md`
- `docs/candi-ref/user-voice-signal-comparison.md`
- `docs/candi-ref/majisemi-article-integration.md`
- `docs/candi-ref/shadcn-and-gantt-constraints.md`
- `docs/candi-ref/adoption-and-recency-reselection.md`
- `docs/candi-ref/demo-comparison-checklist.md`
- `docs/imp/user-judge.md`
- `docs/imp/user-tasks.md`
- `docs/imp/session-discipline.md`
