# Hub Project / Tasks Project データ設計

## 正本と境界

- HubはProjectの名称、説明、順序、状態、候補所属、Hub ↔ Tasks対応を正本とする。
- TasksはProject内のtask、期限、担当、進捗、完了を正本とする。
- `execution_links`は候補単位の外部task linkとして維持する。Project対応をtask linkへ重複保存しない。
- HubはTasksで任意に作られたProjectを自動取込しない。

## `hub_projects`

| field | 型・制約 | 意味 |
| --- | --- | --- |
| `id` | Hub内部ID / primary key | Hub Projectの識別子 |
| `title` | required | Hubで表示・編集する名称 |
| `description` | nullable | Hubで表示・編集する説明 |
| `kind` | `personal` / `project` | 個人常用または個別Project |
| `is_default` | boolean | `personal`かつactiveの一件だけtrue |
| `status` | `active` / `archived` | Hub側の利用状態 |
| `vikunja_project_id` | nullable | 対応するTasks Project ID |
| `vikunja_project_url` | nullable | ブラウザ公開URL。API内部URL・tokenを含めない |
| `link_state` | 下表 | 対応付けの状態 |
| `created_at` / `updated_at` | timestamp | 監査時刻 |

### `link_state`

| 値 | 意味 | GO |
| --- | --- | --- |
| `pending_create` | Hub作成済み、Tasks作成待ちまたは実行中 | 不可 |
| `linked` | Hub / Tasksの一対一対応が確認済み | 可 |
| `failed` | 作成または対応付けに失敗 | 不可。再試行可能 |
| `detached` | 意図的に対応を外した | 不可。再連携可能 |

## 既存テーブルへの追加

- `candidates.hub_project_id`をnullableで追加し、移行完了後の新規候補は必ず一つのHub Projectに所属させる。
- 既存候補への初期所属は、自動backfillしない。明示移行が完了するまではnullを許容する。
- GO時は`candidate.hub_project_id`から`hub_projects.vikunja_project_id`を解決する。旧P0の環境変数だけに依存しない。

## 不変条件

1. activeな`personal`の既定Projectは一件以下。
2. `link_state=linked`なら`vikunja_project_id`と`vikunja_project_url`が存在する。
3. `link_state`が`linked`以外の候補は、Tasks taskを作成できない。
4. 候補とGO先Tasks Projectは同じHub Project対応から解決する。
5. 同じHub Project作成の再試行は、新たなTasks Projectを増やさない。
6. 既存候補、判断、execution linkの件数・hashは、明示的移行操作なしに変化しない。

## 同期しないもの

- Tasks Project名やtask本文をHubの候補・判断へ逆同期しない。
- Tasksで独自作成されたProjectをHubへ作成しない。
- token、Cookie、API内部URLをDB・UI・ログ・受入HTMLへ保存しない。

## 関連正本

- 利用者導線: `docs/product/multi-project-workspace-flow.md`
- API・失敗・再試行: `docs/spec/multi-project-linkage-contract.md`
- コンポーネント境界: `docs/arch/hub-vikunja-multi-project-architecture.md`
