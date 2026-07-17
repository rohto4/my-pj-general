# 2026-07-17 現在地整理・Linux再配信 handoff

## この断面で完了したこと

- Gitは`d1eaaed`（共通候補提案v3とWindows Vault intakeの出力完結性）で`origin/main`と一致していることを確認した。
- `infra/deploy/redeploy-p0-frontend.ps1`をdry-run後に実行し、Hub / Tasksの現行資材をLinuxへsource-only再配信した。Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`、Hub SQLite integrity `ok`を確認した。
- Hub bundle SHA-256は`CB0580D49C147C15B32C6787930CD081AA065F3B1CF5664BD16941F805FECAC7`、Tasks bundle SHA-256は`5C45FB572BC23C1AE765DF9A362A11C499D4BEF47B2F390AA76225E01CE11ABA`である。
- Hubの候補・判断・execution link・取込系テーブルは0件だった。source-only手順はdata/volume/filesを削除せず、実取込、実SQLite書込み、GO、systemd/timer操作をしていない。
- `docs/imp`の実装待ち、利用者受入、受入HTML、星取表、カバレッジ、完了記録、次回焦点を同期した。現在地の正本は`docs/imp/current-state-and-next-discussion-2026-07-17.md`である。

## 再開時の順序

1. `AGENTS.md`の初期読込順を完了する。
2. `docs/imp/current-state-and-next-discussion-2026-07-17.md`と`docs/imp/next-session-focus.md`を読む。
3. P0受入を続けるなら受入HTMLのB02から進む。B02はLinux local LLM unavailableをP0必須とするか、degraded受入とするかの利用者判断である。
4. Slack / Misskeyへ進むなら、`docs/arch/linux-periodic-intake-architecture.md`の固定実装設計を正本にし、fake回帰から確認する。実token・実API・`--commit`・Linux配信・systemd/timerは直前確認を取る。

## 維持するガード

- Windows Ollamaは通常停止する。AI相談はprovider unavailable時に入力・送信・サイド窓口を閉じ、会話保存前の503で拒否する。
- `candidate_proposal.py`と`source_sync.py`を共通経路として使う。独自prompt、legacy direct fallback、自動GOを作らない。
- P0受入とP1 worker有効化・実データ操作を同じcommitへ混ぜない。
- token、secret、Cookie、env全文、source本文を記録・stdout・Gitに出さない。
