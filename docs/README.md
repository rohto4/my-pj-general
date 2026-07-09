# docs Structure

このディレクトリは、要件定義前の比較調査から、将来の設計・運用・実装までを破綻なく蓄積するための入口。

詳細な正本関係、相互更新ルール、タイミング別更新判断表、更新漏れの分析は `docs/guide/docs-management-rules.md` を参照する。
図で把握したい場合は `docs/guide/docs-management-matrix-result-diagram.md` を参照する。

| Path | 役割 |
|---|---|
| `docs/guide/` | 採用済みの運用手順 |
| `docs/spec/` | 確定仕様 |
| `docs/candi-ref/` | 候補 OSS、比較、未採用案 |
| `docs/imp/` | 実装タスク、計画、完了記録 |
| `docs/diary/` | セッション記録 |
| `docs/setting/` | テンプレート、流用元、初期化資料 |
| `docs/ops/` | 運用設計 |
| `docs/product/` | ユースケース、画面、体験設計 |
| `docs/arch/` | システム構成、責務分割 |
| `docs/org/` | ロール、権限、協力体制 |
| `docs/data/` | データモデル、検索、同期 |

## 更新時の基本

- 変更前に正本を決める。
- 正本以外には、要約、リンク、状態だけを同期する。
- タスク整理、進捗、判断待ち、完了、handoff などのタイミング別判断は `docs/guide/docs-management-rules.md` に従う。
- 未決事項、実装待ち、ユーザー判断待ちは `docs/imp/` に集約する。
- セッション記録は `docs/diary/` に置くが、最新状態の正本にはしない。
- 横断ナレッジ更新は `G:\knowledge-vault\knowledge-vault-write-policy.md` を正本にする。
