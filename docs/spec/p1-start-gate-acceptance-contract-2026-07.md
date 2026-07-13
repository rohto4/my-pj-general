# P1開始ゲート・受入・復旧契約 2026-07

## 目的

この文書は、未実装の複数Project連携、認証、PostgreSQL移行を「P0実装済み」と誤認せず、実装を開始できる条件、最初に自動化する検証、実データに進む前の受入・復旧境界を固定する。個別の機能仕様は既存のproduct / data / spec / arch正本を優先する。

## 共通開始条件

1. 対象機能の主正本を読み、未決のユーザー判断と実データ変更を `docs/imp` から分離する。
2. 一時DB・fake外部API・fixtureだけで、成功、重複、通信失敗、再実行、権限拒否を再現する。
3. 既存P0のcandidate、decision、execution link、Vikunja taskを削除、再インポート、暗黙移行しない。
4. 実在するProject作成、既存候補の所属変更、認証を伴う公開、DB接続先の切替は、対象ごとの確認とrollback手順を用意してから行う。

## 機能別の受入契約

| 機能 | 開始ゲート | 最小自動検証 | 失敗時の保持・復旧 | 実データ受入の証跡 |
| --- | --- | --- | --- | --- |
| 複数Project連携 | Hub Projectの所有者・初期Project・既存候補の移行方針が明示済み | 同一idempotency keyの二重送信、外部作成成功後のlink保存失敗、未連携GO拒否、Project A/Bの作成先分離 | Hub Projectを同じIDで`failed`または`pending_create`のまま保持し、同一keyで再試行する。外部Projectを自動削除・自動採用しない | API応答、`hub_projects`、Tasks Project ID/URL、操作IDを照合する |
| 認証・権限 | 二人目または外部協力者への公開要件が発生し、role/scopeが確定 | roleごとのallow/read/deny/confirmをAPIで評価し、UI非表示だけで迂回できないこと。automationのGO拒否 | 不明なactor、scope外、確認なしの外部書込みはdenyし、candidate / decision / taskを変更しない。監査記録から再判定する | owner / collaborator / observer / automationで同じresource-action matrixを実行し、結果と監査IDを保存する |
| PostgreSQL移行 | lock競合、複数writer、認証、1万件規模、またはtransactional outboxの必要性を観測 | 一時PostgreSQLへの繰返し投入、件数・candidate ID・decision・external ID・source lineage・hashの比較、cursor/idempotency再実行 | 差分が1件でもあれば接続先を切替えず、SQLiteを読取可能な正本として残す。外部taskを再作成しない | SQLite integrity、両DBの比較出力、移行ログ、切替前backup、rollback時刻を保存する |

## 実装開始後の完了判定

- 自動検証が通っても、実データ変更、公開、DB切替は完了ではない。各行の実データ受入証跡を満たして初めて次の段階へ進む。
- 失敗・保留は、P0の完成度や設計書化カバレッジを下げず、対応するP1タスクとPoC判定へ記録する。
- UIの見た目・操作感は、機能受入と分けてユーザーが実画面を確認する。ここではrole、状態、API、データ整合、復旧可能性を設計対象とする。

## 関連正本

- 複数Project: `docs/product/multi-project-workspace-flow.md`、`docs/data/hub-project-linkage-data-design.md`、`docs/spec/multi-project-linkage-contract.md`、`docs/arch/hub-vikunja-multi-project-architecture.md`
- 認証: `docs/spec/auth-resource-action-matrix-p1.md`
- PostgreSQL: `docs/spec/postgresql-migration-dry-run-contract-p1.md`
- P1の優先順位・導入ゲート: `docs/product/p1-phase-brief-2026-07.md`
- 進行・PoC判定: `docs/imp/p1-implementation-tasks-2026-07.md`、`docs/imp/p1-poc-readiness-2026-07-12.md`
