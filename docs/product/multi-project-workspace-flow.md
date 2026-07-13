# 複数Project Workspace 要件

## 目的

個人の常用Projectを既定表示にしつつ、仕事・企画・生活など複数のProjectをHubとTasksで安全に扱う。HubはProject、候補、判断、連携状態の正本であり、Tasksは対応するProject内の実行taskの正本である。

## 利用者の導線

1. Hubを開くと、既定の個人Projectを表示する。
2. 利用者はHubでProject名と説明を入力してProjectを作成する。
3. Hubは同じ操作を再試行しても重複しないTasks Projectを作成し、対応を表示する。
4. 候補は一つのHub Projectに所属する。GO時はその対応先Tasks Projectへtaskを作成する。
5. Hubの`Tasks側を開く`は対象Projectまたはtaskが確定している場合に直行する。直接起動など対象が不明な場合はTasksのProject一覧を開く。
6. Tasks側で期限・担当・進捗・完了を操作する。Hubへ戻すのは実行状態のmirrorだけとする。

## Projectの見せ方

- 個人Projectを既定表示にする。既定は一人につき一件だけとする。
- HubのProject一覧は、個人Projectと個別Projectを区別できる。
- Project作成、未連携、作成中、失敗、切り離しは候補判断と別の連携状態として示し、失敗時は再試行を示す。
- 未連携または失敗状態の候補では、GOを安全に止め、別Projectへの誤作成を防ぐ。
- Tasksの左レールでは、現在ProjectのDashboard、List、Gantt、Table、Kanbanを主導線にする。Project、Label、Teamの登録・確認は`マスタ管理`へ集約する。

## 既存データの扱い

- 現在のInbox、候補、判断、execution linkは、自動移行・再作成・再インポートしない。
- 既存候補を個人Projectへ所属させる、Inboxを個人Projectへ対応付ける、既存Projectを再作成する操作は、明示的な移行画面と利用者確認後にだけ行う。
- Project作成・対応付けの導入だけでは、既存件数またはhashを変更しない。

## P0の受入条件

- Hubで作成したProjectとTasks Projectが、ID、表示名、公開URLで一対一に確認できる。
- 同じ作成操作の再試行でTasks Projectが増えない。
- Project Aの候補からProject Bへtaskを作成しない。
- Project作成、未連携、失敗、再試行を表示し、GOできない理由と次の操作が分かる。
- 特定済みのHub導線はTasks Project Dashboardまたはtaskへ、特定不能な直接起動はProject一覧へ到達する。
- 1280px、WQHD、4K縦3分割相当で横overflowを発生させない。

## 関連正本

- 状態・API・冪等性: `docs/spec/multi-project-linkage-contract.md`
- Hubのfield・不変条件: `docs/data/hub-project-linkage-data-design.md`
- コンポーネント・再試行境界: `docs/arch/hub-vikunja-multi-project-architecture.md`
- Thread Line画面要件: `docs/product/thread-line-workspace-requirements.md`
- 実装順・ユーザー確認: `docs/imp/p0-multi-project-linkage-design-2026-07-12.md`
