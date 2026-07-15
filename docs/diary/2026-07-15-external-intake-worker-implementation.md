# 2026-07-15 Slack / Misskey定期worker実装handoff

## 完了した断面

- `docs/arch/linux-periodic-intake-architecture.md`の固定設計に従い、`workers/sync`へHTTP client、Slack collector、Misskey collector、OpenAI互換LLM client、共通proposal pipelineを追加した。
- `run.py`は`--sources slack,misskey`を明示選択とし、外部sourceはdry-run既定である。pending候補とsource run/cursorを書き込むには`--commit`が必要で、GO・Vikunja作成・legacy direct fallbackは行わない。
- Slackは`memo-ideas`の本人root投稿だけ、Misskeyは本人noteだけを正規化する。LLM/HTTPの失敗はsource単位で扱い、partialではcursorを進めない。acceptedだけがpending候補となる。
- fake HTTP / fake LLMと一時SQLiteの23回帰が成功した。実token、実API、Linux実SQLite書込み、source-only配信、systemd登録、timer有効化は実施していない。

## 次に有効化を選ぶ場合

1. `AGENTS.md`の初期読込後、`docs/imp/user-tasks.md`と`docs/imp/next-session-focus.md`を読む。
2. ユーザーがrepo外Linux envへ最小権限のSlack/Misskey設定と初期cursorを用意する。値は読取・表示・Git保存しない。
3. Codexが`--commit`なしの手動dry-runを1回実行し、source別件数と一般化errorだけを確認する。
4. 実データ変更の直前に確認を取り、`--commit`を1回だけ実行する。
5. pending候補の品質を受入後、systemd登録・timer有効化を別の確認として扱う。

## 継続するガードレール

- 実取込、GO、不要、アーカイブ、Vikunja task作成、secret/env設定、Linux配信、systemd操作は勝手に行わない。
- source本文、token、Authorization header、LLM API key、env全文をstdout、journal、DB error、Git、チャットへ出さない。
- P0受入とこのP1 worker実装を同じcommitへ混ぜない。
