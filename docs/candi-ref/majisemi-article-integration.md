# マジセミ記事掲載 OSS の統合評価

## 対象記事

- マジセミ「〖無料で使える〗『プロジェクト管理』ツールまとめ」
- 公開日: 2023-03-02
- URL: https://majisemi.com/topics/tool/3180/

## この記事で挙がっていた OSS / オープンソース系候補

- Taiga
- Redmine
- TaskJuggler
- Focalboard
- Leantime
- Orangescrum
- WeKan
- OpenProject
- ONLYOFFICE Community Server
- Odoo
- ERPNext
- Tuleap
- ProjectLibre
- GanttProject

## 既存 6 件との接続

既存 6 件:

- OpenProject
- Cal.com
- Leantime
- Redmine
- Tuleap
- ProjectLibre

この記事の 14 件のうち、既に主要候補へ入っているもの:

- OpenProject
- Leantime
- Redmine
- Tuleap
- ProjectLibre

この記事から追加検討価値があるもの:

- GanttProject
- Taiga
- Odoo
- ERPNext
- WeKan
- Focalboard
- TaskJuggler
- ONLYOFFICE Community Server
- Orangescrum

## 今回要件との統合評価

評価軸:

- ガント適性
- PJ 管理適性
- スケジュール適性
- 情報入口との相性
- 自前中核 + OSS 借用の戦略との相性

## 残す候補

### GanttProject

- ガント適性: 高い
- PJ 管理適性: 低い
- スケジュール適性: 低い
- 情報入口との相性: 低い
- 判断:
  - `ガント専用の表示思想` を吸う対象として残す
  - ただし desktop 主体なので、Web 閲覧・フォーク前提の本線候補にはしない

### Taiga

- ガント適性: 中
- PJ 管理適性: 高い
- スケジュール適性: 低〜中
- 情報入口との相性: 低い
- 判断:
  - `アジャイル課題管理` の比較対象として残す
  - ただし今回の主価値である入口や自動分別には遠い

### Odoo

- ガント適性: 中
- PJ 管理適性: 高い
- スケジュール適性: 中
- 情報入口との相性: 低〜中
- 判断:
  - `業務スイート全体の中で PM をどう置くか` の参考としては残せる
  - ただし広すぎるため、今回の主候補にはしない

### ERPNext

- ガント適性: 中
- PJ 管理適性: 中〜高
- スケジュール適性: 中
- 情報入口との相性: 低〜中
- 判断:
  - ERP / 業務統合寄りの発想を見る対象としては残せる
  - ただし、やはり広すぎる

### WeKan

- ガント適性: 低い
- PJ 管理適性: 中
- スケジュール適性: 低い
- 情報入口との相性: 中
- 判断:
  - `軽いカード入口` の比較対象としては残せる
  - ただし、今回必要なガントや横断管理には弱い

## 参考止まり

### Focalboard

- Mattermost 連携は魅力だが、ガント優先の今回要件とはずれる
- `Slack 的入口` を考えると発想上の参考にはなる
- ただし、今の本線候補には入れない

### TaskJuggler

- スケジューリング思想は面白い
- ただし UI 借用やダッシュボード借用の対象としては弱い
- 実務比較より、スケジューリング発想の参考止まり

### ONLYOFFICE Community Server

- 文書共同編集の文脈が強い
- 今回の入口、ガント、スケジュール管理の主要求には遠い

### Orangescrum

- 方向性は PM ツールだが、今回の比較軸で際立った位置づけにはなりにくい
- 今回は優先度を落とす

## 今回は外してよい

- `ONLYOFFICE Community Server`
- `TaskJuggler`
- `Orangescrum`

理由:

- 今回のコアである `入口`, `ガント`, `横断管理`, `スケジュール`, `AI 分別` に対して直接の比較価値が低い

## 統合後の候補群

### 主候補

- OpenProject
- Cal.com
- Redmine
- Leantime
- Tuleap
- ProjectLibre

### 補助候補

- GanttProject
- Taiga
- Odoo
- ERPNext
- WeKan

### 参考止まり

- Focalboard
- TaskJuggler
- ONLYOFFICE Community Server
- Orangescrum

## 現時点の実務的な読み

- `ガント` は OpenProject / Redmine / ProjectLibre / GanttProject
- `PJ 管理` は OpenProject / Redmine / Tuleap / Taiga
- `スケジュール` は Cal.com / OpenProject / Redmine
- `入口` は Leantime / WeKan / 自前実装
- `業務スイート視点` は Odoo / ERPNext

## 結論

- 記事の 14 件は一覧としては有用だが、今回の要件にそのまま並列比較するには広すぎる
- あなたの要件では、追加で強く残す価値があるのは `GanttProject`, `Taiga`, `Odoo`, `ERPNext`, `WeKan`
- ただし本線は引き続き `OpenProject`, `Cal.com`, `Redmine`, `Leantime`, `Tuleap`, `ProjectLibre`
- ガントについて `Web 閲覧可能` と `フォークしやすさ` を重視するなら、本線は `OpenProject`、次点で `Redmine`
