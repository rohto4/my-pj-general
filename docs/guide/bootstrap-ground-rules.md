# Bootstrap Ground Rules

## 今回の地盤方針

- 先に要件を固定せず、情報設計と責務分割を先に固める。
- 単一 OSS に全乗せする前提を置かず、UI 統合 + 複数バックエンド併用も許容する。
- 将来の巨大化を前提に、アプリ、サービス、パッケージ、運用知識を初期から分ける。
- ユーザー向け情報と実装者向け情報を `docs/imp/` で分離する。
- PJ docs の更新漏れ防止は `docs/guide/docs-management-rules.md` を正本にする。
- 横断ナレッジ更新判断は `G:\knowledge-vault\knowledge-vault-write-policy.md` を正本にする。

## 流用した資産

- `obsidian-set`: agent 指示の骨格、commands、skills
- `knowledge-vault`: テンプレート、知識蓄積の運用思想
- `my-LLMwiki`: 大きな知識構造を読むための分類発想

## 新PJへ引き継ぐ地盤

新PJへこの運用を移す場合は、`docs/guide/docs-management-rules.md` の「新PJへ引き継ぐ最小ルールセット」を基準にする。
