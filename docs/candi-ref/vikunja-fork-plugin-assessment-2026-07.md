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
- Webhook は失敗時に再試行されないため、pj-general 側は受信イベントを冪等に保存し、定期的な API 照合を後続で用意する。
- self-hostした複数人利用では、Webhook の送信先制限・署名検証を必須にする。
- fork する場合は AGPLv3 の条件を受け入れ、upstream の `main` / release に追随する更新手順と差分管理を先に作る。

## 次の実装順

1. Linux で upstream 無改変の Vikunja 2.3 を自己ホストする。
2. project、API token、Webhook を一つ作る。
3. pj-general の `GO -> Vikunja task作成` を一方向で実装する。
4. `task.updated` / `task.completed` Webhook を受信して SQLite に反映する。
5. 日常利用後、UI差分の要求を一覧化して plugin / fork を判断する。

## 一次情報

- Vikunja plugin development: https://vikunja.io/docs/plugin-development/
- Vikunja plugins: https://vikunja.io/docs/plugins/
- Vikunja webhooks: https://vikunja.io/help/webhooks/
- Vikunja webhooks API: https://vikunja.io/docs/webhooks/
- Vikunja API documentation: https://vikunja.io/docs/api-documentation/
- Vikunja GitHub / license: https://github.com/go-vikunja/vikunja
