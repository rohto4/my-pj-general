# Vikunja fork / plugin 開発の評価

調査日: 2026-07-10

## 結論

Vikunja を `pj-general` の GO 済みタスクの実行基盤候補として優先する。

Vikunja 2.3 には公式プラグイン機構がある。Yaegi による Go ソースの実行時読み込みが推奨され、API route の追加、イベント購読、DB migration が可能である。一方で、機構は実験的で、フロントエンドプラグインは未対応である。

したがって、初期方針は以下にする。

1. `pj-general -> Vikunja` は API による `GO -> task作成` と Webhook による状態通知で接続する。
2. source provenance、候補ID、外部リンク、AI由来の属性など、画面変更不要な機能は Vikunja backend plugin を検討する。
3. TODO 画面のレイアウト、ナビゲーション、詳細pane、独自の操作を変える必要が出た時だけ fork する。
4. まず upstream 無改変の自己ホストを起動し、API / Webhook / plugin の最小検証を終えてから fork を判断する。

## plugin と fork の境界

| 要望 | 推奨手段 | 理由 |
| --- | --- | --- |
| GO済み候補からTODOを作る | API連携 | coreを変更せず、pj-general側で冪等性を持てる |
| タスク状態・期限・担当の更新をpj-generalへ通知する | Webhook | 公式イベントを使える。HMAC署名も利用できる |
| source / candidate ID / AI要約を保存する | APIの説明欄・label・custom metadata、必要ならbackend plugin | 画面改変なしで始められる |
| 独自の検証・イベント処理・追加API | backend plugin | route追加、event listener、migrationが可能 |
| TODO一覧のレイアウトを大きく変える | fork | frontend plugin は未対応 |
| pj-general専用の作業者ホーム、Codex起動ボタン、独自詳細pane | fork または別フロントエンド | UI を一貫して変える必要がある |
| 独自の認可・データモデルを深く変更する | fork | upstream APIだけでは境界を越える |

## 推奨する最初の構成

```text
pj-general
  GO操作
    -> Vikunja REST API: project内に task を作成
    -> candidate_id / vikunja_task_id を保存

Vikunja
  task.created / task.updated / task.completed
    -> signed webhook
    -> pj-general integration endpoint

Vikunja plugin (必要になった時だけ)
  source / AI由来属性の検証
  pj-general向け追加API
  event listener
```

- 最初は `Vikunja API` を正本の作成経路にする。plugin を最初から必須にしない。
- Webhook の再試行挙動はreleaseや送信経路に依存し得る。現行upstreamのE2Eでは失敗時再試行を確認できるが、pj-general側は再試行を前提にせず、受信イベントを冪等に保存し、定期的なAPI照合を用意する。
- self-hostした複数人利用では、Webhook の送信先制限・署名検証を必須にする。
- fork する場合は AGPLv3 の条件を受け入れ、upstream の `main` / release に追随する更新手順と差分管理を先に作る。

## 次の実装順

1. Linux で upstream 無改変の Vikunja 2.3 を自己ホストする。
2. project、API token、Webhook を一つ作る。
3. pj-general の `GO -> Vikunja task作成` を一方向で実装する。
4. `task.updated` / `task.completed` Webhook を受信して SQLite に反映する。
5. 日常利用後、UI差分の要求を一覧化して plugin / fork を判断する。

## 2026-07-11 実機結合後の評価

### 実測した不足と解決方法

| 実測した不足 | 分類 | 解決方法 | plugin / fork |
| --- | --- | --- | --- |
| DockerからLAN公開IPへのAPI接続がtimeout | network | 内部API URLと公開リンクURLを分離 | 不要 |
| private IP宛WebhookがSSRF保護で拒否 | operation / security | 専用network、固定target、private宛許可、HMAC | 不要 |
| Webhook欠落時に状態が戻らない | integration | 再照合APIと履歴をpj-generalへ実装 | 不要 |
| 候補と外部taskの対応が標準Vikunjaにない | data ownership | pj-generalの`execution_links`を正本化 | 不要 |
| 候補ID・出典をtaskから辿りたい | provenance | task descriptionへ候補IDと最小出典を付与 | 不要 |
| pj-general独自の確認待ち・GO UI | UI | pj-generalを別フロントエンドとして維持 | Vikunja fork不要 |
| `GET /tasks/{id}/assignees`が実機で500 | API | task本体の`assignees`参照と割当PUTを使用 | P0では不要、upstream再確認 |
| task更新へ部分payloadを送ると省略fieldが初期化 | API contract | GET後にmutable fieldを保持してPOST | adapterで解決、fork不要 |

### P0判断

- stable `v2.3.0`のAPI v1、Webhook、pj-general側adapterで仮完了範囲を実現できた。
- backend plugin候補は現時点でないため、pluginの最小実装は行わない。
- Vikunja標準TODO画面は実行画面として利用でき、P0でfrontend forkは不要。
- backend forkが必要な権限・状態・コアモデル差分は観測されていない。
- `rohto4/vikunja` forkはupstream追随用に差分なしで保持する。
- 日常利用で標準TODO画面の操作負荷が具体化した場合だけfrontend forkを再評価する。

### upstream追随

- license: AGPL-3.0
- 初回固定release: `v2.3.0`
- 実行物: 公式Docker image `vikunja/vikunja:2.3.0`
- source clone: `G:\devwork\clone-dir\vikunja-upstream`
- fork: `rohto4/vikunja`
- 更新時はrelease notes、API contract、backup、VJ-001〜VJ-015の順で確認する。
- P0ではsource buildを本番経路にせず、forkへ差分を入れる時点でupstream build手順を実行対象にする。

## 一次情報

- Vikunja plugin development: https://vikunja.io/docs/plugin-development/
- Vikunja plugins: https://vikunja.io/docs/plugins/
- Vikunja webhooks: https://vikunja.io/help/webhooks/
- Vikunja webhooks API: https://vikunja.io/docs/webhooks/
- Vikunja API documentation: https://vikunja.io/docs/api-documentation/
- Vikunja GitHub / license: https://github.com/go-vikunja/vikunja
