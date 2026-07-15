# 2026-07-15 AI取込設計・次セッションhandoff

## このhandoffの目的

共通AI候補抽出v2の実装・Linux配信後の状態と、Slack / Misskey定期workerを設計済み・未実装の境界で次セッションへ渡す。次回は設計方式の再検討をせず、ユーザーが実装を選んだ場合だけテスト先行で実装へ進める。

## 完了したこと

- 共通v2 prompt / validatorをknowledge-vault、Slack payload、Misskey payload、AI相談へ適用した。
- `action(kind=todo)`と`aspiration(kind=idea)`を区別し、aspirationの曖昧さ、固有名詞、原文根拠を保持する。全入口はpending候補までで、自動GOしない。
- 実装・設計同期commit`335725c`とLinux配信記録commit`9eac159`は`origin/main`へPush済みである。
- Linux再配信後にHub / Tasks API 200、SQLite integrity `ok`、候補・判断・execution link 0件、Misskey既定無効を確認した。Linux local LLM unavailableはB02の既知項目として残る。
- `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`の責務表を、Windows収集からLinux pendingまでと、利用者確認からGO後Vikunja登録までの2本のMermaidシーケンス図へ置換した。
- `docs/arch/linux-periodic-intake-architecture.md`へ、Slack / Misskey定期workerの実装ファイル、公式API、最小権限、本人filter、pagination、cursor commit、429/5xx、共通v2、partial、dry-run、secret非出力、fake回帰、実データ受入順を固定した。

## 実装済み / 未実装の境界

| 領域 | 状態 |
| --- | --- |
| Windows Vault AI batch | 実装・回帰・Linux配信済み。実Vault pending取込は未実施 |
| Slack payload → 共通v2 → pending | 実装・回帰済み |
| Misskey payload → 共通v2 → pending | 実装・回帰済み、source既定無効 |
| AI相談user本文 → 共通v2提案 | 実装・回帰済み |
| Slack API差分取得 | 設計済み、未実装 |
| Misskey API差分取得 | 設計済み、未実装 |
| 外部source定期workerのLLM / cursor / retry | 設計済み、未実装 |
| 実token・実API・timer | 未設定・未実行 |

## 次に実装する場合の順序

1. `docs/arch/linux-periodic-intake-architecture.md`の固定実装設計を読む。
2. fake Slack / Misskey / LLMの失敗テストを先に追加する。
3. source client、LLM client、共通pipeline、CLIを実装する。
4. dry-run DB不変、`--commit`時だけ書込、partial時cursor据置、冪等性、secret非出力を回帰する。
5. systemd/env例を同期するが、timerは有効化しない。
6. 実サービス確認は、ユーザーがrepo外へ最小権限tokenを設定した後、dry-run 1回、明示確認、commit 1回、品質受入、timer有効化の順に分ける。

## 次セッションで勝手に行わないこと

- 実候補作成、GO、Vikunja task作成、既存データ削除、再インポート
- Slack app / token、Misskey tokenの作成・表示・Git保存
- Linux配信、systemd登録・有効化、env全文表示
- P0受入作業とP1 worker実装の同一commit化
- legacy direct importへのfallback

## 再開プロンプト

```text
G:\devwork\pj-general の作業を前セッションから引き継いでください。

最初にAGENTS.mdの指示どおり、AGENTS.md、PROJECT.md、tech-stack.md、README.md、docs/imp/user-tasks.md、必要なimp文書をファイル実体から読み直してください。その後、docs/imp/next-session-focus.mdとdocs/diary/2026-07-15-external-intake-worker-handoff.mdを読んで現在地を復元してください。

共通AI候補抽出v2とWindows knowledge-vault AI batchは実装・回帰・Linux配信済みです。Slack / Misskeyはpayload以降だけ実装済みで、外部API取得と定期workerは未実装ですが、docs/arch/linux-periodic-intake-architecture.mdの「Slack / Misskey定期workerの固定実装設計」に実装方式を確定済みです。方式比較へ戻らず、この設計を正本にしてください。

まずgit statusとorigin/mainとの差分を確認し、P0受入を続けるか、Slack / Misskey worker実装へ進むかを最新のユーザー指示から判断してください。worker実装の場合はTDDでfake HTTP / fake LLMから開始し、実token・実API・実SQLite・Linux配信・timer有効化は使わないでください。candidate_proposal.pyとsource_sync.pyを再利用し、独自prompt、legacy direct fallback、自動GOを作らないでください。

実データ変更、外部書込み、Linux配信、systemd有効化は直前に確認を取り、P0受入とP1実装を同じcommitへ混ぜないでください。状態・タスク・設計・完了記録をdocs管理ルールに従って同期し、検証後にrohto4/my-pj-generalのmainへcommit/pushしてください。
```
