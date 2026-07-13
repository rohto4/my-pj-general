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
| `docs/imp/current-goal-and-data-structure-brief-2026-07-11.md` | 完了済みUI作業の履歴ブリーフ |
| `docs/diary/` | セッション記録 |
| `docs/setting/` | テンプレート、流用元、初期化資料 |
| `docs/ops/` | 運用設計 |
| `docs/product/` | ユースケース、画面、体験設計 |
| `docs/arch/` | システム構成、責務分割 |
| `docs/org/` | ロール、権限、協力体制 |
| `docs/data/` | データモデル、検索、同期 |

## Vikunja結合資料

- Linuxサーバー構築手順: docs/guide/linux-server-setup-for-vikunja.md
- Linux起動雛形: `infra/vikunja/`

- アーキテクチャ: `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
- Linux配置・運用: `docs/arch/vikunja-linux-deployment-and-operations-2026-07.md`
- API結合契約: `docs/spec/vikunja-integration-contract-2026-07.md`
- 実機受入試験: `docs/spec/vikunja-integration-acceptance-tests-2026-07.md`
- 設計レビュー: `docs/imp/vikunja-design-review-2026-07-11.md`
- 実機検証結果: `docs/imp/vikunja-integration-verification-2026-07-11.md`
- データ設計: `docs/data/vikunja-integration-data-design-2026-07.md`
- タスク: `docs/imp/vikunja-integration-tasks.md`
- Hub / Vikunjaフロント受入: `docs/imp/p0-frontend-completion-tasks-2026-07-12.md`
- Thread Line Workspace画面・ブランド要件: `docs/product/thread-line-workspace-requirements.md`
- Hub UI操作契約: `docs/spec/hub-ui-interaction-contract-p0.md`
- Thread Line Tasks UI契約: `docs/spec/thread-line-tasks-ui-contract-p0.md`
- 複数Project Workspace要件: `docs/product/multi-project-workspace-flow.md`
- Hub Project / Tasks Projectデータ設計: `docs/data/hub-project-linkage-data-design.md`
- 複数Project連携契約: `docs/spec/multi-project-linkage-contract.md`
- 複数Project連携アーキテクチャ: `docs/arch/hub-vikunja-multi-project-architecture.md`
- 設計書化カバレッジ（HTML星取表）: `docs/imp/design-documentation-coverage-assessment-2026-07-13.html`
- 役割別の最小読込ガイド: `docs/guide/implementation-context-reading-guide.md`
- コンテキスト圧迫・セッション切替ガイド: `docs/guide/context-pressure-session-guideline.md`
- 現行ゴール・データ構造ブリーフ: `docs/imp/current-goal-and-data-structure-brief-2026-07-11.md`
- P0・連結状態監査: `docs/imp/p0-status-audit-2026-07-11.md`
- P0完了監査 2026-07-12: `docs/imp/p0-completion-audit-2026-07-12.md`
- P0運用・backup・rollback: `docs/ops/p0-operations-runbook-2026-07.md`
- Linux Listening Lounge配信手順: `docs/guide/linux-listening-lounge-deploy.md`
- Linux定期入口同期アーキテクチャ: `docs/arch/linux-periodic-intake-architecture.md`
- P1フェーズブリーフ: `docs/product/p1-phase-brief-2026-07.md`
- P1候補評価: `docs/candi-ref/p1-candidate-evaluation-2026-07.md`
- P1実装タスク: `docs/imp/p1-implementation-tasks-2026-07.md`
- P1 PoC readiness: `docs/imp/p1-poc-readiness-2026-07-12.md`
- P1 verification matrix: `docs/imp/p1-verification-matrix-2026-07-12.md`
- P1完了監査: `docs/imp/p1-completion-audit-2026-07-12.md`
- P0 / P1完成度評価（HTML星取表）: `docs/imp/p0-p1-completion-assessment-2026-07-12.html`
- P0フロント受入追加タスク: `docs/imp/p0-frontend-completion-tasks-2026-07-12.md`
- 次の目標（P0フロント受入完了）: `docs/imp/next-goal-p0-frontend-completion-2026-07-12.md`
- 次の目標（P1実機運用仕上げ・P0完了後）: `docs/imp/next-goal-p1-real-operations-finish-2026-07-12.md`
- セッション引継ぎ: `docs/diary/2026-07-12-session-handoff.md`
- 別セッション用再開プロンプト: `docs/diary/2026-07-12-resume-prompt.md`
- P1認証resource-action matrix: `docs/spec/auth-resource-action-matrix-p1.md`
- P1 PostgreSQL migration dry-run契約: `docs/spec/postgresql-migration-dry-run-contract-p1.md`
- ローカルLLM相談窓口要件: `docs/product/local-llm-chat-intake-2026-07.md`
- ローカルLLM相談窓口データ設計: `docs/data/local-llm-chat-data-design-2026-07.md`
- ローカルLLM相談窓口タスク: `docs/imp/local-llm-chat-intake-tasks.md`
- Vikunja frontend dashboard fork計画: `docs/candi-ref/vikunja-frontend-fork-dashboard-plan-2026-07.md`
- Vikunja frontend dashboard forkタスク: `docs/imp/vikunja-dashboard-fork-tasks.md`
- 2026-07-12 P0 UI / fork継続監査: `docs/diary/2026-07-12-p0-ui-and-fork-audit.md`
- 開始Diary: `docs/diary/2026-07-10-vikunja-integration-plan.md`

## 更新時の基本

- 変更前に正本を決める。
- 正本以外には、要約、リンク、状態だけを同期する。
- タスク整理、進捗、判断待ち、完了、handoff などのタイミング別判断は `docs/guide/docs-management-rules.md` に従う。
- 未決事項、実装待ち、ユーザー判断待ちは `docs/imp/` に集約する。
- セッション記録は `docs/diary/` に置くが、最新状態の正本にはしない。
- 横断ナレッジ更新は `G:\knowledge-vault\knowledge-vault-write-policy.md` を正本にする。
