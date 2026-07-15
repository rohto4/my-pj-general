# P0ブロッカー監査 2026-07-15

## 結論

P0のコード上の未実装と最新版配信は、今回のWindows knowledge-vault AI batchの実装・Linux反映で解消した。残るのは、Linux HubのチャットLLM到達性、ユーザーの視覚承認、実データを作る受入操作である。P1機能はP0ブロッカーへ混ぜない。

## 実機観測

2026-07-15のLinux再配信後に常設環境をread-onlyで確認した。

| 対象 | 状態 | 証拠 |
| --- | --- | --- |
| Hub health | `degraded` | `/api/health` |
| SQLite | `ok` / integrity `ok` / 290,816 bytes | candidates 0、decisions 0、execution links 0、source sync runs 1 |
| Vikunja | `ok` / task 0 | `/api/health`、`/api/integrations/vikunja/overview` |
| Linux Hubのlocal LLM | `unavailable` / `gemma4:latest` | `/api/health`。chatだけに影響 |
| Windows local LLM | `gemma4:latest`利用可能 | `/api/tags`と合成Markdown collector実行 |
| Vault AI batch | Linux配信・schema反映済み、実Vault dry-run完了 | 新table 5件は0行。3文書、3 accepted、2 held、1文書fallback。実候補変更なし |

## P0受入チェックへの統合

B01〜B05の実行順、現在結果、コメント、詳細受入行への導線は、[上から実行するP0受入チェック](p0-frontend-acceptance-checklist-2026-07-12.html)を正本とする。この監査には表を重複保持せず、ブロッカーの分類根拠と完了証拠だけを残す。

- B01は完了済みとして先頭に表示する。
- B02はLLM到達性回復または縮退受入のユーザー判断を記録する。
- B03はR06/R07、RV01〜RV05、U05の全承認後に閉じる。
- B04はU03の確認付き実データ操作と同一operation ID照合後に閉じる。
- B05は`実取込GO`後の初回Vault AI batch品質確認で閉じ、自動GOは行わない。

## 非ブロッカーとして完了したもの

- Windows Vault collector、秘密らしい行の伏せ、OpenAI互換ローカルLLM呼出。
- 精度優先prompt、完全一致引用、タグmaster、日付、完了事項、曖昧titleのvalidator。
- LLM停止時の明示action限定fallback。
- manifest SHA-256、専用SSH鍵、Linux単独SQLite writer。
- batch/document/fragment/AI run/proposalのlineageとaccepted提案のpending候補化。
- batch再送の冪等性、既存GO/Vikunja境界の維持。
- 設計正本、読込ガイド、カバレッジ表、レビュー結果表への同期。

## 元要求に対する完了証拠

| 要求 | 正本・実装 | 検証結果 |
| --- | --- | --- |
| Windows VaultからLinux SQLiteまでの経路設計 | `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`、`docs/spec/knowledge-vault-ai-intake-contract-p0.md`、`docs/data/knowledge-vault-ai-intake-data-design-2026-07.md`、`docs/ops/knowledge-vault-ai-intake-runbook-2026-07.md` | Windows reader / Linux単独writer / pending止まりの境界を静的回帰で確認 |
| 4入口共通の精度優先候補提案prompt | `apps/web/prompts/threadline-candidate-proposal-v3.txt`、`apps/web/candidate_proposal.py`、`apps/web/vault_intake.py` | action / aspiration、完全一致引用、aspiration非具体化、完了除外、タグ・日付、秘密らしい行、LLM失敗時action限定fallbackを自動回帰。v3の実Vault 1文書dry-runはaccepted 2 / held 0 / fallback 0で、実データ品質はB05で受入する |
| 小規模なら実装まで | Windows collector、OpenAI互換LLM client、validator、SSH batch、Linux importer、SQLite lineage 5table | Hub Node 49件、Hub Python 19件、worker / infra 23件が成功。Linux Hub / Tasks API 200、SQLite integrity `ok` |
| その他P0のブロッカー検出と非ブロック実装 | この監査、`docs/imp/imp-tasks.md`、P0完成度表 | B01とコード上の未実装は完了。B02〜B05は外部構成判断、視覚承認、確認付き実データ操作へ限定 |

## P0完了条件

1. B01は完了。Linux SQLiteに新tableが存在し既存データを破壊していない。
2. B02はチャットをP0必須とするなら到達性を回復し、必須でない判断なら明示的に縮退受入する。
3. B03をユーザーが承認する。
4. B04とB05を実行前確認付きで各1件受入し、誤登録・二重登録がない。
