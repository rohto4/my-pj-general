# Hub複数Project / Tasks Project アーキテクチャ

## 構成

```text
Hub Project UI
  -> Hub API / SQLite hub_projects
     -> Vikunja adapter (idempotent Project create)
        -> Tasks Project
Candidate / decision UI
  -> Hub API resolves hub_project_id
     -> execution_links
        -> Tasks task
Tasks webhook / reconcile
  -> execution_task_state mirror only
     -> Hub read model
```

## 責務分割

| コンポーネント | 責務 | 持たない責務 |
| --- | --- | --- |
| Hub UI | Project選択・作成確認、候補所属表示、連携失敗と再試行の表示 | Tasks taskの直接編集、勝手な移行 |
| Hub API / SQLite | Hub Project、候補所属、連携state、操作ID、idempotency keyの正本 | Tasksのtask field正本 |
| Vikunja adapter | Tasks Project作成、公開URL解決、task作成先の指定、失敗の正規化 | Hub Projectの自動取込 |
| Tasks | Project内task、期限、担当、進捗、完了 | Hub候補・判断の編集 |
| Webhook / reconcile | execution task stateのHub mirror | 候補本文・判断・Project所属の逆同期 |

## 冪等性と障害境界

- Project作成要求にはHub Projectに紐づく再利用可能なidempotency keyを使う。
- Hub側で`pending_create`を先に確定し、成功後だけ`linked`へ進める。タイムアウト時に新規Hub Projectを作り直さない。
- Adapter障害、Vikunja API障害、公開URL未解決は`failed`として保持する。再試行は同一Hub Projectを対象にする。
- GOはHub Projectが`linked`であることを前提にする。未連携時はtask作成APIを呼ばない。
- 再照合・webhookはtask状態を更新できるが、Project対応を勝手に変更しない。

## 運用境界

- P0の既存SQLite件数・hashが0件または不一致でない限り、再インポート・自動移行をしない。
- Project作成、既存Inbox対応付け、既存候補の所属設定は実データ変更であり、利用者確認後にのみ実行する。
- Linux再配信はsource-only bundle、hash照合、API 200、integrity/count確認を守る。既存の安全再配信runbookを使用する。

## 関連正本

- 体験要件: `docs/product/multi-project-workspace-flow.md`
- データ: `docs/data/hub-project-linkage-data-design.md`
- API契約: `docs/spec/multi-project-linkage-contract.md`
- 現行単一Project連携: `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
