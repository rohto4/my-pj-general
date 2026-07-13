# Vikunja frontend dashboard fork タスク

## 2026-07-12 大幅UX改修追加

ユーザーフィードバックにより、配色・角丸・dashboard追加だけでは不十分と判定した。P1では次をforkの正式スコープへ追加する。

- [ ] 各ページの目的、入力、操作結果、次の一手を画面内に表示する
- [ ] 「何もない」を空白で表現せず、意味・作成操作・別view導線を持つempty guideへ変更する
- [ ] Dashboard / Inbox / List / Table / Kanban / Gantt / task detailの役割を説明する
- [ ] page guideを共通component化し、viewごとの文言だけを定義する
- [ ] guideを折りたたみ可能にし、日常利用の情報密度を壊さない
- [ ] 既存API・認証・権限・task modelを変更せず、実データ操作を維持する
- [ ] narrow 1280px / wide 1920pxで実データ・空状態・操作後を監査する

作成日: 2026-07-11

## 実装タスク

- [x] fork clone、upstream remote、基準commit、frontend build境界を確認する
- [x] Hubとのデータ所有権と導線境界を確認する
- [x] dashboardの固定期間と日付なしtaskの扱いを定義する
- [x] `codex/pj-general-dashboard` branchを作成する
- [x] `/projects/:projectId/dashboard` routeを追加する
- [x] Task APIのページングを使うdashboard data loaderを追加する
- [x] summary / recent tasks / 30日calendar / undated tasksを追加する
- [x] ProjectWrapperからdashboardへ遷移する導線を追加する
- [x] unit testとdate boundaryのテストを追加する
- [x] dashboard date unit testを実行する（4件成功）
- [x] fork差分のlintを実行する（エラー0、警告のみ）
- [x] production buildを実行する（成功）
- [ ] frontend全体typecheckを通す（upstream既存の `ProjectWrapper.vue` / `router/index.ts` 等の型エラーで未完了。新規dashboard/date実装には該当エラーなし）
- [ ] custom image buildとLinux別tag起動を確認する（SSH鍵認証待ち）
- [x] custom image build / image切替の再実行スクリプトを `infra/vikunja/` に固定する
- [ ] HubのTasks側リンクをdashboard URLへ切り替えるか判断する
- [ ] Hub / Tasksの並列画面を確認し、微調整を記録する

## 2026-07-12 Listening Lounge テーマ統一

- [x] 既存dashboard branchから `codex/vikunja-listening-lounge` worktree / branchを作成した
- [x] Hubと共通のink / indigo / copper / wool tokenをVikunja frontendへ追加した
- [x] navbar / sidebar / content / card / task / table / dropdown / form / loginを共通theme layerで統一した
- [x] panel / card / button / input / select / dropdownの構造角丸を0pxへ統一した
- [x] dashboard control / view linkの角丸を0pxへ変更した
- [x] browser theme colorとPWA manifestをListening Lounge色へ変更した
- [x] theme unit test、全unit test、stylelint、production buildを実行した
- [x] 改善前のhome / project list / sort / filter / task detailを実Vikunjaで撮影した
- [x] 改善後のloginを1280px / 1920pxで撮影した
- [x] `codex/pj-general-dashboard` をListening Lounge実装までfast-forwardし、本流branchへ昇格した
- [x] 改善後の認証済みhome / dashboard / list / sort / filter / task detailを実データで撮影する
- [x] Table / Kanban / Ganttを実データで追加撮影する
- [x] 認証済み画面のスクリーンショット監査を反映して最終調整する
- [x] production previewからVue DevToolsを除外し、開発UI・警告表示なしで最終撮影する
- [ ] custom image buildとLinux別tag起動を確認する

2026-07-12の再検証では、page guide / empty guide / project guide / themeの対象unit test 24件、Listening Lounge themeのstylelint、frontend production buildを通過した。build時のSass deprecationとupstream依存由来のRolldown annotation warningは残るが、build終了コードは0である。全unit testをVitestの既定globで実行するとPlaywright e2e specを誤って取り込むため、unit対象を明示して検証する。

実装commit:

- `883f9a6b6` (`feat: align frontend with Threadline listening lounge`)
- `2daff1e0c` (`style: refine task detail lounge surfaces`)
- `325bc5475` (`style: polish production lounge review surfaces`)

本流branch `codex/pj-general-dashboard` は `325bc5475` までfast-forward済み。

比較スクリーンショットと監査結果は `tmp/ui-review/vikunja-listening-lounge/README.md` に集約する。

## 受入条件

- Vikunjaの既存taskを追加のHub DBなしでdashboardに表示できる。
- taskが0件、日付なし、期限のみ、期間あり、完了済みの各状態を表示できる。
- 今日から30日のカレンダーが初期表示される。
- 既存List / Table / Kanban / Ganttへの導線を壊さない。
- backend API、認証、権限、Webhook契約を変更しない。
- custom frontend imageのbuild・起動・rollback手順がある。

## 2026-07-12 保存状態

- 実装branch: `codex/pj-general-dashboard`
- local commit: `325bc5475` (`rohto4` author、Listening Lounge最終監査反映済み)
- GitHub originへのlocal pushはWindows credential providerの `SEC_E_NO_CREDENTIALS`、GitHub connector経由のbranch作成は `403 Resource not accessible by integration` で失敗。実装はlocal commit `325bc5475` に保存済み。

## custom imageの切替・rollback手順

Vikunjaの既存Dockerfileがfrontend distをbackendへembedするため、fork rootで次のbuildを行う。

```sh
docker build --build-arg RELEASE_VERSION=2.3.0-pj-general-dashboard \
  -t rohto4/vikunja:2.3.0-pj-general-dashboard .
```

`infra/vikunja/compose.example.yaml` は `VIKUNJA_IMAGE` を指定した場合だけcustom imageへ切り替え、未指定時はstable `vikunja/vikunja:2.3.0` を使う。rollbackは `VIKUNJA_IMAGE=vikunja/vikunja:2.3.0` に戻して再作成する。

再現可能なbuildと切替は次のスクリプトを使う。

```sh
VIKUNJA_SOURCE_DIR=/srv/pj-general/build/vikunja-listening-lounge \
  /srv/pj-general/infra/vikunja/build-listening-lounge.sh
/srv/pj-general/infra/vikunja/switch-image.sh \
  rohto4/vikunja:2.3.0-pj-general-listening-lounge
```

rollbackはcustom imageのデータvolumeを変更せず、次だけを実行する。

```sh
/srv/pj-general/infra/vikunja/switch-image.sh vikunja/vikunja:2.3.0
```

2026-07-12時点では、LinuxサーバーへSSH接続できず、このbuild・起動・rollbackの実機確認だけが未完了である。
