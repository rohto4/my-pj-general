# P0 プロンプトテンプレート管理仕様

作成日: 2026-07-10

## 目的

P0 で Codex 起動支援、候補整理、GO 後作成に使うプロンプトテンプレートの最小管理仕様を定義する。

プロンプトテンプレートは、ユーザーが確認待ち候補から次の作業へ移るときの引き継ぎ文を安定させるために使う。

## 初期テンプレート

| ID | 名前 | 対象 | 用途 |
| --- | --- | --- | --- |
| `codex-start` | Codex起動支援 | candidate | 選択候補を実装タスクとして開始する |
| `candidate-triage` | 候補整理 | intake | 4入口の本人本文をaction / aspirationへ分ける現行方針を管理画面で要約表示する |

`candidate-triage`の管理画面本文は運用方針の短い表示であり、LLMへ渡す全文promptではない。版管理されたruntime正本は`apps/web/prompts/threadline-candidate-proposal-v3.txt`、入力・出力・validator契約は`docs/spec/ai-candidate-proposal-contract-p0.md`とする。管理画面の本文編集でruntime promptを差し替えない。
| `go-promotion` | GO後作成 | decision | GOした候補をタスク、予定候補、判断記録へ展開する |

## 管理画面で見る項目

| 項目 | P0 動作 |
| --- | --- |
| 名前 | テンプレート名 |
| 対象 | `candidate` / `intake` / `decision` |
| 本文 | P0 では短文表示 |
| 有効 / 無効 | SQLite の `enabled` で保持 |

## P0 で作らないこと

- 複雑な変数エディタ。
- テンプレートの履歴管理。
- モデル別プロンプト切替。
- 複数エージェント向け profile。

## 実装対応

- SQLite: `prompt_templates`
- UI: 管理画面 `プロンプトテンプレート`
- API: `/api/bootstrap`
