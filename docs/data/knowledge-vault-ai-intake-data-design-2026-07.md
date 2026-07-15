# knowledge-vault AI取込データ設計 2026-07

## 正本と目的

Vault原文はWindowsの`G:\knowledge-vault`が正本である。Linux Hub SQLiteは、取り込んだ時点の許可断片、hash、AI処理結果、候補への写像を再現する監査倉庫とする。実行TODOの正本は引き続きGO後のVikunjaである。

## batch v1

`threadline.knowledge-vault.batch.v1`は次を持つ。

- batch: `schema_version`、`batch_id`、`created_at`、`source_root_label`、`prompt_version`、`model`、`stats`
- document: `document_id`、`relative_path`、`scope`、`content_hash`、`modified_at`、`summary`、`fragments`、`ai_run`
- fragment: `fragment_id`、`heading`、`line_start`、`line_end`、`excerpt`、`content_hash`、`extraction_method`
- proposal: `proposal_id`、`title`、`summary`、`todo`、`kind`、`schedule`、`confidence`、`missing`、`tags`、`evidence_quotes`、`validation`

batch IDは、schema version、prompt version、model、document IDsをcanonical JSONにしてSHA-256から生成する。manifestはbatchファイル全体のSHA-256を別ファイルに持つ。

## SQLite table

| Table | 主キー・一意性 | 保存内容 |
| --- | --- | --- |
| `intake_batches` | `batch_id` | version、source、prompt/model、manifest hash、state、件数、取込時刻 |
| `source_documents` | `document_id` | 相対path、scope、content hash、mtime、文書要約、収集metadata |
| `source_fragments` | `fragment_id` | 文書ID、見出し、行範囲、許可断片、fragment hash、抽出方式 |
| `ai_runs` | `run_id` | batch/document、provider/model、prompt version、input/output hash、状態、一般化error |
| `candidate_proposals` | `proposal_id` | 提案field、根拠、validation、status、candidate ID |

## 不変条件

- `source_documents.source_ref`はVault相対pathで、Windows user名や絶対rootを保存しない。
- 同一相対pathでもcontent hashが変われば別document IDとし、過去snapshotを追跡できる。
- fragment excerptはLLMへ渡した許可範囲だけとし、全文を無条件保存しない。
- evidence quoteは同じdocumentの保存fragmentに完全一致する。
- accepted proposalだけが1件のcandidateへ写像され、`candidate_proposals.candidate_id`で逆引きできる。
- batch再送は行数を増やさない。別batchでも同じproposal IDならcandidateを増やさない。
- `ai_runs`にはhidden reasoningを保存しない。入力/出力hash、構造化結果、一般化errorだけを持つ。
- candidateを不要/アーカイブしてもlineageを削除しない。

## 保持・削除

P0は明示的な自動削除を行わない。Vaultから原文が消えても監査snapshotは残す。将来、保持期間を設ける場合は、candidateとdecisionから参照されるlineageを先に削除しない。
