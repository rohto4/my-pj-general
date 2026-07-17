# 次セッションの焦点

> 最新handoffは`docs/diary/2026-07-17-current-state-and-linux-redeploy-handoff.md`。圧縮・セッション移動後はhandoffより先に`AGENTS.md`の初期読込順を実行する。

## 現在地

- 共通AI候補抽出v3はknowledge-vault / Slack payload / Misskey payload / AI相談へ実装済みで、`action`と`aspiration`を原文根拠付きで分ける。全入口はpending止まりで、自動GOしない。
- Windows knowledge-vault AI batchはcollector・LLM・validator・SSH・Linux importer・lineage・冪等性まで実装、回帰、Linux配信済み。実Vault batchのpending取込はユーザー確認待ちである。
- `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`は責務表を2本のMermaidシーケンス図へ変更し、明示light theme・boxなし・下側actorなしで再描画済みである。`docs/spec/ai-candidate-proposal-contract-p0.md`には共通v3 promptのPython/Node組込・実行位置図がある。
- Slack / Misskeyは、payload以降に加え外部API差分取得・共通v3 LLM・cursor・retry・dry-run既定のworker実装とfake回帰を完了した。実token・実API・Linux実SQLite書込み・配信・systemd登録・timer有効化は未実施である。
- Linux Hub / Tasksは`d1eaaed`を含む2026-07-17時点の資材へsource-only再配信済み。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、SQLite integrity `ok`、候補・判断・execution link・取込系テーブル0件を確認済み。Linux local LLM unavailableはB02の既知判断待ちである。
- WindowsのOllamaは、普段のブラウザ利用を優先して通常は停止する。AI相談は`config.availability=unavailable`で入力・送信・サイド窓口を閉じ、保存前503で拒否する。v3のローカルdry-run後は停止済みとし、次の実取込前にだけユーザー許可で起動する。
- P0の優先順位は変わらない。`docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html`のB02、B03、B04、B05とRV/U項目がユーザー受入として残る。
- 通常のHub / Tasks source-only再配信は、登録済み専用鍵を使ってCodexが直接実行する。ユーザーにPowerShell一行を依頼せず、sudo、secret/env、実データ変更だけをユーザー境界へ戻す。

## 次セッションの開始順

1. `AGENTS.md`、`PROJECT.md`、`tech-stack.md`、`README.md`、`docs/imp/user-tasks.md`を実体から読む。
2. `docs/guide/implementation-context-reading-guide.md`の「P0入口・候補・AI相談」を使う。
3. `docs/imp/current-state-and-next-discussion-2026-07-17.md`と`docs/diary/2026-07-17-current-state-and-linux-redeploy-handoff.md`を読む。
4. ユーザーがP0受入を続ける場合は受入HTMLの先頭未完了項目から進む。
5. ユーザーがSlack / Misskey worker有効化を選ぶ場合だけ、repo外env設定後の手動dry-run 1回へ進む。実データ変更となる`--commit`、Linux配信、systemd登録・timer有効化はそれぞれ直前確認を取る。

## Slack / Misskey worker有効化計画

1. `docs/arch/linux-periodic-intake-architecture.md`の「Slack / Misskey定期workerの固定実装設計」を正本にする。方式比較へ戻らない。
2. `workers/sync/test_external_intake.py`と`test_run.py`のfake回帰を再実行する。実サービス、実token、Linux SQLiteは使わない。
3. repo外envへ最小権限tokenと初期cursorを設定する作業はユーザーが行う。値は表示・保存しない。
4. Codexが`--commit`なしの手動dry-runを1回行い、件数と一般化errorだけを確認する。
5. 実データ変更を明示して確認後、手動`--commit`を1回だけ実行し、pending候補の品質受入後にtimer有効化を別途確認する。

## ガードレール

- 実データを変更するGO、不要、アーカイブ、Vault batch commit、Slack / Misskey `--commit`は直前確認を取る。
- token、secret、Cookie、env全文、source本文をGit・stdout・journal・チャットへ出さない。
- Slackは`memo-ideas`の本人投稿だけ、Misskeyは本人noteだけを対象にする。
- LLM失敗時にlegacy direct importへ落とさず、cursorを進めない。
- P0受入とP1 worker実装を同じcommitへ混ぜない。
