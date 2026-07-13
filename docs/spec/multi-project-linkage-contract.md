# Hub複数Project / Tasks Project 連携契約

## 目的

Hub Project作成、Tasks Project冪等作成、候補所属、GO先解決、失敗・再試行を、既存P0の候補判断・task作成契約と分離して定義する。

## Project作成

1. 利用者はHubでProject名称・説明・kindを入力し、作成を確定する。
2. Hubは`hub_projects`を`pending_create`で作成する。
3. Hubは同じHub Projectを識別するidempotency keyでTasks Project作成を要求する。
4. 成功時はTasks Project IDと公開URLを保存し、`link_state=linked`にする。
5. 失敗時はHub Projectを保持し、`link_state=failed`と再試行可能な理由を表示する。

- API再試行、通信切断、同時クリックのいずれでも、同じHub Projectに対応するTasks Projectは一件だけとする。
- Project作成の確定後にTasks作成を実行する。Tasks側の孤立ProjectをHubへ自動採用しない。

## GO先解決

1. Hubは候補の`hub_project_id`を取得する。
2. 対応するHub Projectが`linked`であることを確認する。
3. `vikunja_project_id`をGO登録先として解決する。
4. 既存`execution_links`がある場合は新規taskを作成せず、同じtask linkを返す。
5. 解決できない場合はGOを止め、未連携または失敗の状態と再試行導線を返す。

- Project Aの候補からProject BのTasks Projectへtaskを作成してはならない。
- Hubからtask本文・候補判断を逆同期しない。TasksからHubへ戻すのはexecution state mirrorだけとする。

## 再試行・切離し

| 状態 | 利用者に見せる操作 | 再試行の結果 |
| --- | --- | --- |
| `pending_create` | 作成中表示、必要時は更新 | 同じHub Projectの状態を再照合 |
| `failed` | 失敗理由、再試行 | 同じidempotency keyでTasks作成を再要求 |
| `detached` | 未連携理由、再連携 | 新しい対応要求を明示的に開始 |
| `linked` | Tasksを開く | 対象Project Dashboardへ遷移 |

- 再試行の失敗は候補の判断ログに混在させない。Project連携状態として記録する。
- 既存Inbox、候補、判断、execution linkの移行は別操作とし、本契約の通常作成・再試行では実行しない。

## 受入

- Project作成、二重送信、通信失敗後再試行、GO先解決、未連携GO停止、対象不明のTasks直接起動をそれぞれ検証する。
- API応答、Hub画面、DBの`hub_projects`、Tasks Project ID/URLを同一操作IDで照合する。
- 実在Project作成、既存候補の所属変更、Inbox対応付けは実データ変更のため、操作前に利用者確認を得る。

## 関連正本

- field・不変条件: `docs/data/hub-project-linkage-data-design.md`
- 利用者導線: `docs/product/multi-project-workspace-flow.md`
- 構成・worker責務: `docs/arch/hub-vikunja-multi-project-architecture.md`
- 既存の単一Project GO契約: `docs/spec/vikunja-integration-contract-2026-07.md`
