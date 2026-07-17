# 現在地と次の実装検討（2026-07-17）

この文書は、P0受入・外部worker有効化・実データ操作を混同しないための現在地である。恒久的な仕様は各`docs/spec`・`docs/arch`を正本とし、ここには進捗と開始条件だけを置く。

## 固定済みの実装断面

| 領域 | 実装・検証済み | まだ行わないこと |
| --- | --- | --- |
| 共通AI候補抽出 | v3 prompt、`candidate_proposal.py`、`source_sync.py`、pending止まり、fake回帰 | 独自prompt、legacy direct fallback、自動GO |
| Windows Vault batch | collector、LLM、validator、SSH/Linux importer、lineage、冪等性、fake回帰、実Vault 1文書のdry-run | 実batch取込、Linux SQLite書込み、候補/GO作成 |
| AI相談 | provider停止時の入力・送信・サイド窓口クローズ、保存前503、Node/Python回帰 | Ollama常駐、停止中の会話保存 |
| Slack / Misskey worker | 外部API collector、cursor/retry、共通v3 pipeline、`--sources`/`--commit`、fake HTTP/fake LLM回帰 | 実token、実API、Linux配信、実SQLite、systemd登録、timer有効化 |
| Linux Hub / Tasks | source-only deploy、hash照合、rebuild、Hub/Tasks API 200、Hub SQLite integrity `ok` | volume/files削除、再import、secret/env表示、実データ変更 |

## 2026-07-17 の配信証跡

- Git断面: `d1eaaed`、実行前に`origin/main`との差分は0/0だった。
- Hub bundle SHA-256: `CB0580D49C147C15B32C6787930CD081AA065F3B1CF5664BD16941F805FECAC7`。
- Tasks bundle SHA-256: `5C45FB572BC23C1AE765DF9A362A11C499D4BEF47B2F390AA76225E01CE11ABA`。
- Hub `/api/bootstrap=200`、Tasks `/api/v1/info=200`。Hub DBはintegrity `ok`、候補・判断・execution link・取込系テーブルは0件だった。
- Linux local LLMは`unavailable`。Windows Ollamaは通常停止方針のままであり、この配信は起動していない。

## 割り込みタスクの整理

### P0受入（ユーザー操作・判断）

1. B02で、local LLMをP0必須として回復するか、`degraded`の縮退受入にするか決める。
2. B03で、R06/R07、RV01〜RV05、U05の見た目・操作感を受入する。今回の再配信で資材状態は更新済みだが、視覚受入は未判定のまま。
3. B04/U03は、実データ変更の直前確認後に1操作だけ実行し、HTTP・操作ID・判断ログを照合する。
4. B05は、`prompt-v2-v3-comparison-2026-07-16.html`のレビュー後に、改めて実取込GOを受けて1 batchだけ実行する。

### Slack / Misskey worker（P1有効化）

- 実装とfake回帰は完了している。方式比較は再開しない。
- 開始条件は、利用者がrepo外envへ最小権限tokenと初期cursorを設定すること。
- 実行順は、fake回帰再確認 → 実APIの`--commit`なしdry-run 1回 → 明示確認後の`--commit` 1回 → 候補品質受入後のtimer有効化である。
- Linux配信、実SQLite書込み、systemd登録、timer有効化はそれぞれ別の実データ/運用境界であり、P0受入と同じcommitや同じ操作に混ぜない。

## 次の実装検討に入るための入口

- P0を優先する場合: `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` のB02から再開する。
- worker有効化を検討する場合: `docs/arch/linux-periodic-intake-architecture.md` の「Slack / Misskey定期workerの固定実装設計」と`docs/imp/user-tasks.md`の後続節だけを読む。
- P1の新規テーマを検討する場合: `docs/imp/user-judge.md` と`docs/product/p1-phase-brief-2026-07.md`を読む。P0未受入を完了扱いにせず、決定前のP1コードは始めない。

## 明示的に未実行の境界

実Vault import、候補のGO/不要/アーカイブ、Slack/Misskeyの実API・実token、Linux実SQLite書込み、systemd登録、timer有効化、Ollama常駐は、この状態整理・再配信には含まれない。
