# P0追加: Hub複数ProjectとVikunja Project連携 実装タスク

## 正本

- 利用者導線: `docs/product/multi-project-workspace-flow.md`
- field・不変条件: `docs/data/hub-project-linkage-data-design.md`
- API・冪等性・再試行: `docs/spec/multi-project-linkage-contract.md`
- コンポーネント・障害境界: `docs/arch/hub-vikunja-multi-project-architecture.md`

この文書は実装順、受入、実データ変更前の確認だけを扱う。仕様本文をここへ重複しない。

## 実装順

1. SQLite migrationで`hub_projects`と`candidates.hub_project_id`を追加する。既存候補は自動backfillしない。
2. Hub APIにProject一覧・作成・再試行・対応状態のread modelを追加する。
3. Vikunja adapterに、Hub Project IDをidempotency keyとするTasks Project作成・公開URL解決を追加する。
4. Hub UIに個人Project既定表示、Project作成、link state、失敗再試行、対象別Tasks導線を追加する。
5. GO先を環境変数ではなく`candidate.hub_project_id`から解決する。
6. Project作成、重複送信、失敗再試行、未連携GO停止、Project誤作成防止を回帰へ追加する。
7. Linux再配信後に、実Project作成を行う前に利用者確認を得て受入する。

## P0受入

- [ ] Hubで個人Projectと個別Projectを区別して表示する。
- [ ] Project作成後、Hub ID、Tasks Project ID、表示名、公開URLを一対一に照合する。
- [ ] 二重送信と通信失敗後の再試行でTasks Projectが重複しない。
- [ ] Project Aの候補からProject Bへtaskを作成しない。
- [ ] 未連携・失敗・切離しの候補でGOが安全に止まり、再試行導線が見える。
- [ ] 特定済みのHub導線はTasks Project Dashboardまたはtaskへ、特定不能な直接起動はProject一覧へ進む。
- [ ] 既存候補、判断、execution linkの件数・hashが、明示移行なしに変化しない。

## 利用者確認が必要な実データ操作

- 現在のInboxを個人Projectへ明示対応付けするか。
- 新Project作成を、Tasks Project作成まで一回の確定操作にするか、Hub作成後の`Tasksへ連携`を分けるか。
- 既存候補を初回個人Projectへ一括所属させるか、未所属として一件ずつ選ぶか。

上記を確定するまで、migrationの本番適用、既存データ移行、実Tasks Project作成を実行しない。
