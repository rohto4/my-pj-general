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

コンテキスト自動圧縮、セッション移動、handoff 受領、または要約コンテキストからの再開を検知した場合は、ユーザーへの通常回答や作業継続より前に、以下の初期化ファイル群を再読み込みする。圧縮後の要約だけで文脈補強を済ませず、必ずファイル実体を読む。

1. `AGENTS.md`
2. `PROJECT.md`
3. `tech-stack.md`
4. `README.md`
5. `docs/imp/user-tasks.md`
6. 必要に応じて `docs/imp/user-judge.md`
7. 必要に応じて `docs/imp/imp-tasks.md`
8. `docs/guide/implementation-context-reading-guide.md` を読み、作業役割に対応する最小読込セットを選ぶ
9. 必要に応じて `docs/imp/imp-plan.md`
10. 必要に応じて `docs/diary/*`
11. 必要に応じて `docs/spec/*`
12. 必要に応じて `docs/candi-ref/*`
13. 必要に応じて `.agents/skills/*/SKILL.md`
14. 必要に応じて `commands/*.md`

役割別読込ガイドで対象外の実装ツリーを先に広く読まない。設計書だけで状態・操作・境界を断定できない場合は、`docs/imp/design-documentation-coverage-assessment-2026-07-13.html`に示す対象実装だけを読む。不足事実は先に`docs/imp/imp-tasks.md`へ記録し、該当する設計正本へ補完する。

## コンテキスト圧迫とセッション切替

- 圧縮回数、実入力 token、画像・添付・巨大 tool 出力を診断する場合だけ、`docs/guide/context-pressure-session-guideline.md` と `.agents/skills/audit-context-pressure/` を使う。これは通常の初期読込セットには加えない。
- 圧縮後は必須初期化と現行タスクを再読込し、圧縮が2回以上、または次の局面が画像・長大出力を伴う場合は、docs と Git の断面を閉じて新しいセッションへ移る。

## AGENTS.md 非対応環境

- AGENTS.md を自動で読まない LLM / tool を使う場合は、作業開始時にこの `AGENTS.md` を明示的に読ませる。
- 共通起動ルールはこの `AGENTS.md` を正本にし、セッション固有の handoff は `docs/diary/*` と `docs/imp/*` に置く。

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

## docs 相互更新ルール

- PJ docs の更新判断は `docs/guide/docs-management-rules.md` を正本にする。
- 仕様更新だけでなく、タスク整理、タスク進捗、判断待ち発生、判断待ち解消、完了、handoff 作成の各タイミングで、同文書のタイミング別更新判断表に従う。
- `AGENTS.md` には詳細判断表を重複記載しない。実行時の必須ルールだけを置く。
- `PROJECT.md` は PJ 固有の目的、スコープ、正本関係、恒久的な構造、採用済みの重要判断を示す場所であり、タスク、進捗、次走テーマ、セッション履歴、判断材料の生ログ、参照元一覧を書かない。
- タスク、進捗、判断待ち、完了記録は `docs/imp/*`、セッション履歴や handoff は `docs/diary/*`、候補・比較・参照元は `docs/candi-ref/*` または `docs/setting/*`、採用判断の根拠は該当する `docs/arch/*` / `docs/spec/*` / `docs/product/*` / `tech-stack.md` に置く。

## 割り込み・実装断面・Git履歴

- 大きな割り込み判断は、まず `docs/imp/*` に次タスクとして記録する。緊急停止を除き、進行中の実装を途中で別目的へ切り替えない。
- 作業の切替前に、進行中の最小単位をテスト、実装/設計文書、配信artifact、未完了・ブロッカー表示まで同期し、再開可能な断面へ閉じる。
- 断面を閉じた後に、その単位だけをGit commitとして残す。未検証の新機能、実データ変更、別目的のリファクタリングを同じcommitへ混在させない。
- 割り込みが実データ変更を伴う場合は、既存断面を閉じた後に、操作前の確認を得てから着手する。

## `docs/imp/` の命名

- `imp-*`: 実装者向け。計画、実装待ち、完了記録、技術判断。
- `user-*`: ユーザー向け。判断待ち、確認事項、実機作業。
- ユーザーが見るべき内容は `user-*` で追える状態にする。

## 横断ナレッジの扱い

- 横断ナレッジ vault は `G:\knowledge-vault`。
- この PJ 固有の設計、比較、進行状態はこの PJ 内を正本にする。
- タスク整理、進捗、判断待ち、判断解消、完了、handoff などの各タイミングで、`G:\knowledge-vault` への反映要否を評価する。
- 反映対象は、再利用できる知見、比較結果、判断原則、運用ルール、失敗知、後から復元価値のある作業記録とする。
- `G:\knowledge-vault` 配下の既存カテゴリへ蓄積し、新しい知見倉庫は増やさない。
- 反映先と粒度は `G:\knowledge-vault\knowledge-vault-write-policy.md` に従う。
- ここでのタスク完了は、最終成果物の完成だけでなく、エージェントが自律走行中に作った TODO / サブタスクを消化した単位を含む。
- `G:\knowledge-vault` へ記載する前に、必ず `G:\knowledge-vault\knowledge-vault-write-policy.md` を読む。
- knowledge-vault への反映要否は、`docs/guide/docs-management-rules.md` の knowledge-vault 判定ゲートと中央 policy の両方で判断する。

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

## knowledge-vault への知識蓄積

- `G:\knowledge-vault` は横断ナレッジの正本であり、この PJ からも他 PJ からも共通の知識蓄積先として扱う。
- `G:\knowledge-vault` へ記載する場合は、事前に `G:\knowledge-vault\knowledge-vault-write-policy.md` を読み、保存先、記載粒度、書かないものを判断する。
- この PJ の `AGENTS.md` には詳細ルールを重複記載しない。知識蓄積ルールの更新は `G:\knowledge-vault\knowledge-vault-write-policy.md` に集約する。

## 回答方針

- 通常回答は短く、結論と次の行動を優先する。
- 大規模設計では、境界、依存、将来の分割可能性を明示する。
- 最新情報や外部 OSS の仕様は、必要時に一次情報で確認してから扱う。
