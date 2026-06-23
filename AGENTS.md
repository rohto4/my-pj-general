# PJ-General Agent Instructions

## 最優先ルール

1. 日本語で対応する。
2. すべてのファイルは UTF-8 として読み書きする。
3. この PJ は、個人の予定、個人タスク、組織タスク、協力者タスク、やりたいこと、判断記録、知識を一元管理するサイトを作る拠点として扱う。
4. まだ要件は確定していないため、初期段階では仕様を断定せず、情報設計、運用設計、比較材料の整備を優先する。
5. secret、トークン、Cookie、未公開の認証情報をリポジトリに書かない。
6. 大規模化を前提に、1ファイル1責務、境界の明確化、将来の分割容易性を優先する。
7. この PJ の開発運用は当面 Codex 専用として設計し、マルチエージェント対応は別PJまたは後続フェーズで扱う。

## この PJ の役割

- 個人活動とチーム活動を一元管理する Web サイトの設計・実装拠点
- 要件整理前の比較検討、OSS 選定、統合設計の正本
- 将来 100 万行規模まで伸びても破綻しにくいモノレポ運用の土台
- Codex を主作業エージェントとして使う前提の開発拠点

## 読み込み順

1. `AGENTS.md`
2. `PROJECT.md`
3. `chat-init.md`
4. `README.md`
5. `docs/imp/user-tasks.md`
6. 必要に応じて `docs/imp/user-judge.md`
7. 必要に応じて `docs/imp/imp-tasks.md`
8. 必要に応じて `docs/imp/imp-plan.md`
9. 必要に応じて `docs/spec/*`
10. 必要に応じて `docs/candi-ref/*`
11. 必要に応じて `.agents/skills/*/SKILL.md`
12. 必要に応じて `commands/*.md`

## `chat-init.md` の位置づけ

- `chat-init.md` は、毎チャットの最初に読む共通初期化ファイルとして扱う。
- 現状の進行状況やセッション固有の handoff は書かず、毎回共通で効く起動前提、出力方針、更新方針のみを置く。
- セッション依存の内容は `docs/diary/*` や `docs/imp/*` に置き、`chat-init.md` には混ぜない。

## ディレクトリ方針

- `apps/`: エンドユーザー向けアプリケーション。Web、admin、mobile-web など。
- `services/`: BFF、API、認証、通知、同期など独立サービス。
- `packages/`: ドメインモデル、UI、SDK、共通ライブラリ。
- `workers/`: バッチ、ジョブ、インデクサ、AI 補助処理。
- `plugins/`: 将来の拡張モジュールや外部統合。
- `infra/`: IaC、デプロイ、監視、権限設計。
- `docs/`: 仕様、運用、候補比較、実装計画、議事録。

## docs の使い分け

- `docs/guide/`: 採用済みの運用手順・作業ガイド
- `docs/spec/`: 確定仕様、データモデル、権限制約、API 前提
- `docs/candi-ref/`: 候補 OSS、比較表、未採用案、調査メモ
- `docs/imp/`: 実装タスク、計画、完了記録、ユーザー依頼待ち
- `docs/diary/`: セッション記録、handoff
- `docs/setting/`: テンプレート、流用元、初期設定資料
- `docs/ops/`: 日次運用、保守、監査、サポート運用
- `docs/product/`: ユースケース、画面方針、体験設計
- `docs/arch/`: システム構成、責務分割、統合方針
- `docs/org/`: 権限、ロール、組織運用
- `docs/data/`: データモデル、イベント、検索、同期

## `docs/imp/` の命名

- `imp-*`: 実装者向け。計画、実装待ち、完了記録、技術判断。
- `user-*`: ユーザー向け。判断待ち、確認事項、実機作業。
- ユーザーが見るべき内容は `user-*` で追える状態にする。

## 横断ナレッジの扱い

- 横断ナレッジ vault は `G:\knowledge-vault`。
- この PJ 固有の設計、比較、進行状態はこの PJ 内を正本にする。
- 複数 PJ で再利用できる知見、比較結果、判断原則のみ `G:\knowledge-vault` へ反映する。
- `G:\knowledge-vault` 配下の既存カテゴリへ蓄積し、新しい知見倉庫は増やさない。
- 以後も横断価値のある判断や運用知識は、都度 `G:\knowledge-vault` に反映する。

## 初期流用元

- agent / project テンプレート: `obsidian-set`, `knowledge-vault`, `my-LLMwiki`
- skills / commands: `G:\devwork\obsidian-set`
- 情報基盤テンプレート: `G:\knowledge-vault\templates`
- Codex 運用参照: `G:\devwork\clone-dir\aaif-goose-goose`
- MCP 実装参照: `G:\devwork\clone-dir\PrefectHQ-fastmcp`
- MCP 参照サーバ群: `G:\devwork\clone-dir\modelcontextprotocol-servers`

## エージェント方針

- 当面は Codex 専用で運用する。
- 他モデル向けの互換層や agent profile は、この PJ では先に抱え込まない。
- 将来のマルチエージェント対応は別PJまたは後続タスクとして切り出して管理する。

## 現行 Codex 土台

- `aaif-goose/goose` を、Codex 向け運用土台の単独追随先として扱う。
- `PrefectHQ/fastmcp` の `fastmcp-client-cli` skill は利用可能だが、土台の追随先ではなく MCP 実装時の参考として扱う。
- `modelcontextprotocol/servers` は本番実装ではなく参照実装集として扱い、設計判断の根拠に使う。
- 外部 repo の流用だけで閉じず、必要な skill は Codex で内製し、この PJ に追加していく前提で扱う。

## 回答方針

- 通常回答は短く、結論と次の行動を優先する。
- 大規模設計では、境界、依存、将来の分割可能性を明示する。
- 最新情報や外部 OSS の仕様は、必要時に一次情報で確認してから扱う。
