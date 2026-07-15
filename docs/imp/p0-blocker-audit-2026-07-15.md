# P0ブロッカー監査 2026-07-15

## 結論

P0のコード上の未実装は、今回のWindows knowledge-vault AI batchで解消した。残るのは、最新版配信、Linux HubのチャットLLM到達性、ユーザーの視覚承認、実データを作る受入操作である。P1機能はP0ブロッカーへ混ぜない。

## 実機観測

2026-07-15 10:04 JSTにLinux常設環境をread-onlyで確認した。

| 対象 | 状態 | 証拠 |
| --- | --- | --- |
| Hub health | `degraded` | `/api/health` |
| SQLite | `ok` / integrity `ok` / 290,816 bytes | candidates 0、decisions 0、execution links 0、source sync runs 1 |
| Vikunja | `ok` / task 0 | `/api/health`、`/api/integrations/vikunja/overview` |
| Linux Hubのlocal LLM | `unavailable` / `gemma4:latest` | `/api/health`。chatだけに影響 |
| Windows local LLM | `gemma4:latest`利用可能 | `/api/tags`と合成Markdown collector実行 |
| Vault AI batch | local実装・回帰・実Vault dry-run完了、Linux未配信 | 3文書、3 accepted、2 held、1文書fallback。実DB変更なし |

## ブロッカー表

| ID | 項目 | 種別 | 現在地 | 次操作 |
| --- | --- | --- | --- | --- |
| B01 | 最新Hub sourceのLinux反映 | Codex実行可能 | 新schema/importer/promptはローカルのみ | テスト・commit/push後、安全な再配信scriptで反映しhealth/schemaを確認する |
| B02 | Hub対話チャットのLLM到達性 | 外部状態・構成判断 | Linuxからconfigured providerへ到達不可。Windows localhostのLLMは利用可能 | Windows LLMを認証・firewall付きLAN endpointにするか、Linux側runtimeを置くかを別途決める。P0の他機能は止めない |
| B03 | R05/R06/R07、RV01〜RV05、U05 | ユーザー視覚判断 | source/fork回帰と直近配信は完了、最終見た目・操作感は未承認 | 受入HTMLで実画面判定する |
| B04 | U03 GO / 編集 / 不要 / アーカイブ | ユーザー確認付き実データ操作 | DBは空。実装とoperation ID回帰は完了 | 実行前確認後、同一operation IDをHTTP・画面・SQLiteで照合する |
| B05 | Vault AI batch初回実取込 | ユーザー確認付き実データ操作 | dry-runのみ。Linux DBと候補は未変更 | 最新Hub配信後、確認を得て1batch取込し、pending候補品質をレビューする。GOはしない |

## 非ブロッカーとして完了したもの

- Windows Vault collector、秘密らしい行の伏せ、OpenAI互換ローカルLLM呼出。
- 精度優先prompt、完全一致引用、タグmaster、日付、完了事項、曖昧titleのvalidator。
- LLM停止時の明示action限定fallback。
- manifest SHA-256、専用SSH鍵、Linux単独SQLite writer。
- batch/document/fragment/AI run/proposalのlineageとaccepted提案のpending候補化。
- batch再送の冪等性、既存GO/Vikunja境界の維持。
- 設計正本、読込ガイド、カバレッジ表、レビュー結果表への同期。

## P0完了条件

1. B01を閉じ、Linux SQLiteに新tableが存在し既存データを破壊していない。
2. B02はチャットをP0必須とするなら到達性を回復し、必須でない判断なら明示的に縮退受入する。
3. B03をユーザーが承認する。
4. B04とB05を実行前確認付きで各1件受入し、誤登録・二重登録がない。
