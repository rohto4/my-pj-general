# knowledge-vault AI取込runbook 2026-07

候補提案は`apps/web/prompts/threadline-candidate-proposal-v3.txt`を使う。v2と旧v1 promptは過去batchの監査用であり、新規取込へ指定しない。action / aspirationの判定とheld条件は`docs/spec/ai-candidate-proposal-contract-p0.md`を正本とする。

## 安全境界

- Windows collectorはVaultをread-onlyで扱う。
- Linux SQLiteはHub container内の`db_tool.py`だけが書く。
- SSH専用鍵を使い、`BatchMode=yes`、`IdentitiesOnly=yes`を指定する。
- 実行前後にSQLiteを削除・復元・転送しない。既存candidate、decision、Vikunja taskを一括削除しない。
- API key、env全文、秘密鍵、原文全文をログへ表示しない。

## 初回dry-run

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File G:\devwork\pj-general\infra\intake\import-knowledge-vault.ps1 `
  -IdentityFile "$env:USERPROFILE\.ssh\codex_pjserver_ed25519" -NoLlm -DryRun
```

dry-runでは対象件数、提案件数、fallback件数、batch/manifest pathとSHA-256だけを表示する。本文、promptへ渡した原文、secretは表示しない。

## LLM付き実行

ローカルLLMのOpenAI互換endpointとmodelを指定する。API keyが必要な場合は`LOCAL_LLM_API_KEY`環境変数だけで渡す。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File G:\devwork\pj-general\infra\intake\import-knowledge-vault.ps1 `
  -IdentityFile "$env:USERPROFILE\.ssh\codex_pjserver_ed25519" `
  -LlmBaseUrl "http://127.0.0.1:11434/v1" -LlmModel "<local-model>"
```

collectorが失敗した場合は転送しない。LLMだけが失敗した場合は規則ベースfallbackをbatchへ記録し、処理を継続する。LLMなしを失敗扱いにしたい検証時だけ`-RequireLlm`を使う。

## 成功確認

1. PowerShell結果の`batchId`、`created`、`held`、`duplicate`だけを確認する。
2. Hub `/api/observability`で`knowledge_vault_batch`の最新runが`succeeded`であることを確認する。
3. Hub確認待ちで新規候補の相対path、根拠抜粋、要約、TODOを確認する。
4. GOは自動では行わない。実データを変更するGO/不要/アーカイブは既存受入手順に従う。

## 復旧

| 症状 | 対応 |
| --- | --- |
| LLM接続不可 | `-NoLlm`で明示actionだけを収集するか、endpoint復旧後に同じVaultを再実行する |
| 不正JSON・根拠不一致 | held理由をtest/SQLiteで確認し、promptまたはmodelを修正する。手動でacceptedへ書き換えない |
| manifest不一致 | importを停止し、Windowsでbatchを再生成・再転送する |
| SSH失敗 | 専用鍵、公開鍵、`BatchMode`、接続先を確認する。パスワードをscriptへ保存しない |
| import途中失敗 | transaction rollbackを確認し、同じbatchを再送する |
| 重複送信 | `duplicate=true`は正常。既存candidateを削除しない |

## 定期化ゲート

手動で3回以上、誤候補率・修正率・重複0件を確認してからWindows Task Schedulerへ登録する。LLM品質は30〜50件の正解セットで、schema成功100%、根拠一致95%以上、不要候補10%以下、秘密混入0件を目安にする。合格しても自動GOは導入しない。
