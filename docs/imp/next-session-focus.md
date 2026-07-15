# 次セッションの焦点

> 最新handoffは`docs/diary/2026-07-15-external-intake-worker-handoff.md`。圧縮・セッション移動後はhandoffより先に`AGENTS.md`の初期読込順を実行する。

## 現在地

- 共通AI候補抽出v2はknowledge-vault / Slack payload / Misskey payload / AI相談へ実装済みで、`action`と`aspiration`を原文根拠付きで分ける。全入口はpending止まりで、自動GOしない。
- Windows knowledge-vault AI batchはcollector・LLM・validator・SSH・Linux importer・lineage・冪等性まで実装、回帰、Linux配信済み。実Vault batchのpending取込はユーザー確認待ちである。
- `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`は責務表を2本のMermaidシーケンス図へ変更し、明示light theme・boxなし・下側actorなしで再描画済みである。`docs/spec/ai-candidate-proposal-contract-p0.md`には共通v2 promptのPython/Node組込・実行位置図がある。
- Slack / Misskeyはpayload以降だけ実装済み。外部API取得と定期workerは未実装だが、`docs/arch/linux-periodic-intake-architecture.md`へ実装ファイル、API、cursor、retry、dry-run、テスト、受入順まで固定した。
- Linux Hub / Tasksは最新配信済み。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、SQLite integrity `ok`、候補・判断・execution link 0件を確認済み。Linux local LLM unavailableはB02の既知判断待ちである。
- P0の優先順位は変わらない。`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`のB02、B03、B04、B05とRV/U項目がユーザー受入として残る。
- 通常のHub / Tasks source-only再配信は、登録済み専用鍵を使ってCodexが直接実行する。ユーザーにPowerShell一行を依頼せず、sudo、secret/env、実データ変更だけをユーザー境界へ戻す。

## 次セッションの開始順

1. `AGENTS.md`、`PROJECT.md`、`tech-stack.md`、`README.md`、`docs/imp/user-tasks.md`を実体から読む。
2. `docs/guide/implementation-context-reading-guide.md`の「P0入口・候補・AI相談」を使う。
3. このファイルと`docs/diary/2026-07-15-external-intake-worker-handoff.md`を読む。
4. ユーザーがP0受入を続ける場合は受入HTMLの先頭未完了項目から進む。
5. ユーザーがSlack / Misskey worker実装を指示した場合だけ、下記の実装計画へ進む。

## Slack / Misskey worker実装計画

1. `docs/arch/linux-periodic-intake-architecture.md`の「Slack / Misskey定期workerの固定実装設計」を正本にする。方式比較へ戻らない。
2. TDDでfake HTTP / fake LLMテストを先に作る。実サービス、実token、Linux SQLiteは使わない。
3. `workers/sync/http_client.py`、`slack_collector.py`、`misskey_collector.py`、`llm_client.py`、`proposal_pipeline.py`を追加し、`run.py`を`--sources`とdry-run既定・`--commit`明示へ更新する。
4. `candidate_proposal.py`と`source_sync.py`を再利用し、独自prompt、独自validator、legacy direct fallbackを作らない。
5. fake回帰完了後にsystemd/env例を同期する。source-only安全再配信はCodexが直接行えるが、実token、実取込、systemd登録・timer有効化はユーザー確認なしに行わない。

## ガードレール

- 実データを変更するGO、不要、アーカイブ、Vault batch commit、Slack / Misskey `--commit`は直前確認を取る。
- token、secret、Cookie、env全文、source本文をGit・stdout・journal・チャットへ出さない。
- Slackは`memo-ideas`の本人投稿だけ、Misskeyは本人noteだけを対象にする。
- LLM失敗時にlegacy direct importへ落とさず、cursorを進めない。
- P0受入とP1 worker実装を同じcommitへ混ぜない。
