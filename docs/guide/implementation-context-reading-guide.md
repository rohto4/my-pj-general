# 実装コンテキスト読込ガイド

## 目的

実装前に広いソースツリーを読む代わりに、担当する機能の正本設計と受入根拠だけを先に読む。設計書に答えがないときだけ、`docs/imp/design-documentation-coverage-assessment-2026-07-13.html` が示す実装境界へ進む。

この文書は読込範囲のガイドであり、プロダクト・仕様・データ・構成・運用の本文を重複して持たない。文書の置き場所と更新ルールは `docs/guide/docs-management-rules.md` を正本とする。

## 共通の初期化とリンクの扱い

コンテキスト圧縮・handoff後は、まず `AGENTS.md` が必須とする `AGENTS.md` / `PROJECT.md` / `tech-stack.md` / `README.md` / `docs/imp/user-tasks.md` を読む。2026-07-13時点で 751行・約44KB（実測約13,472 token、256Kの約5.3%）であり、これは共通の安全・目的・現行P0・実行入口・ユーザー操作境界を復元するための上限とする。

- `docs/imp/imp-tasks.md` は、実装・設計書化・進行タスクに着手するときだけ、対象タスクの見出しを読む。ユーザー受入だけなら常時読まない。
- `docs/imp/user-judge.md`、`docs/imp/imp-plan.md`、diary、`docs/spec/*`、skills、commands は `AGENTS.md` のとおり必要時だけ読む。
- カバレッジHTMLは、対象機能の行名を検索して、そこに記載された正本・証跡・実装境界だけを選ぶ。HTML全体のCSS・JavaScriptや、別機能の行を読む必要はない。
- **文書中のリンクは自動読込キューではない。** 現在の作業で不足している証拠種別（体験、状態/API、データ、外部境界、運用、受入/回帰）を補うリンクだけを開く。リンク先のリンクを再帰的に全読込しない。
- 長い文書は、対象見出しとその直下の節だけを読む。別節または全文を読むのは、対象節で状態・操作・境界を断定できない場合だけにする。

上記を読んだ後に、作業と無関係な `apps/web`、Vikunja fork、過去diaryを横断検索しない。必要な設計本文が不足している場合は、先にカバレッジHTMLの該当行を黄色または赤にし、`docs/imp/imp-tasks.md` へ不足を記録する。

## P0 Hub UI

最小読込セット:

1. `docs/product/thread-line-workspace-requirements.md`
2. `docs/spec/screen-structure-p0.md`
3. `docs/spec/confirmation-queue-p0.md`（候補・判断を触る場合）
4. 画面受入・回帰を行う場合だけ `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` の対象ID
5. カバレッジHTMLの「Hub画面・左レール」行だけ

実装を読む条件:

- 設計書が対象操作の状態遷移、アンカー、表示責務を定義していない。
- 受入と回帰が矛盾し、`apps/web/test/api.test.mjs` の期待を確認する必要がある。
- この場合だけ `apps/web/index.html`、`apps/web/app.js`、`apps/web/styles.css` を対象順に読む。APIの意味が必要なときだけ `apps/web/server.mjs` と `apps/web/db_tool.py` を追加する。

## Vikunja / Tasks UI

最小読込セット:

1. `docs/product/thread-line-workspace-requirements.md`
2. `docs/spec/thread-line-tasks-ui-contract-p0.md`
3. `docs/imp/p0-vikunja-ux-remediation-2026-07-12.md`
4. 画面受入・回帰を行う場合だけ `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` の対象ID
5. カバレッジHTMLの「Thread Line Tasks UI」行だけ

実装を読む条件:

- 画面契約にないselector、上流Vikunjaの制約、または既存forkの回帰失敗を確認する必要がある。
- この場合だけ `tmp/vikunja-listening-lounge/frontend/src` の対象view・component・styleを読む。fork全体を先に読むことはしない。

## Hub ↔ Vikunja連携

最小読込セット:

1. `docs/arch/vikunja-pj-general-integration-architecture-2026-07.md`
2. `docs/spec/vikunja-integration-contract-2026-07.md`
3. `docs/data/vikunja-integration-data-design-2026-07.md`
4. 受入・回帰を行う場合だけ `docs/spec/vikunja-integration-acceptance-tests-2026-07.md`
5. カバレッジHTMLの「Hub ↔ Vikunja連携」行だけ

実装を読む条件:

- API payload、Webhook dedupe、再照合、または表示mirrorの実装根拠が契約にない。
- この場合だけ `apps/web/vikunja_adapter.py`、`apps/web/server.mjs`、対応する `apps/web/test/test_vikunja_adapter.py` を読む。

## P0入口・候補・AI相談

最小読込セット:

1. `docs/spec/intake-source-adapters.md`（Web / vault / Slackの現行P0入口）
2. AI候補判定を触る場合だけ `docs/spec/ai-candidate-proposal-contract-p0.md`
3. `docs/spec/confirmation-queue-p0.md`（候補の判断、operation ID、GO失敗）
4. AI相談を触る場合だけ `docs/spec/local-llm-chat-runtime-contract-p0.md`、`docs/product/local-llm-chat-intake-2026-07.md`、`docs/data/local-llm-chat-data-design-2026-07.md`
5. Windows Vault AI batchを触る場合だけ `docs/arch/windows-vault-ai-intake-architecture-2026-07.md`、`docs/spec/knowledge-vault-ai-intake-contract-p0.md`、`docs/data/knowledge-vault-ai-intake-data-design-2026-07.md`、`docs/ops/knowledge-vault-ai-intake-runbook-2026-07.md`
6. Slack / Misskey定期workerを触る場合だけ `docs/arch/linux-periodic-intake-architecture.md` の「Slack / Misskey定期workerの固定実装設計」
7. 障害・復旧を扱う場合だけ `docs/ops/p0-operations-runbook-2026-07.md`
8. カバレッジHTMLの「入口取込・ソース同期」「Windows Vault AI batch」「Hub候補・判断」「ローカルLLM相談」の対象行だけ

実装を読む条件:

- candidateへの写像、source run、操作ID、provider HTTP status、tool scopeのいずれかが正本にない。
- 共通AI判定は`apps/web/candidate_proposal.py`と`apps/web/prompts/threadline-candidate-proposal-v2.txt`、legacy scanとSlack/Misskey写像は`apps/web/source_sync.py`、Windows batchは`apps/web/vault_intake.py`と`infra/intake/*`、SQLite/HTTPは`apps/web/db_tool.py` / `apps/web/server.mjs`を読む。定期workerは上記archで指定した`workers/sync`の対象ファイルだけをテスト先行で追加する。testは`test_candidate_proposal.py` / `test_source_sync.py` / `test_vault_intake.py` / `api.test.mjs`とworker新規testの対象だけを読む。

## P1開始設計

最小読込セット:

1. `docs/spec/p1-start-gate-acceptance-contract-2026-07.md`
2. 複数Projectなら `docs/product/multi-project-workspace-flow.md`、`docs/data/hub-project-linkage-data-design.md`、`docs/spec/multi-project-linkage-contract.md`、`docs/arch/hub-vikunja-multi-project-architecture.md`
3. 認証なら `docs/spec/auth-resource-action-matrix-p1.md`、PostgreSQLなら `docs/spec/postgresql-migration-dry-run-contract-p1.md`
4. `docs/product/p1-phase-brief-2026-07.md` の導入ゲート
5. カバレッジHTMLの「複数Project連携」または「P1認証・PostgreSQL移行」の対象行だけ

実装を読む条件:

- P1開始ゲートを満たし、fake APIまたは一時DBの最小実装に入る。
- P0 source、実在Project、既存candidate、既存Vikunja taskを先に広く読んだり変更したりしない。

## Linux配信・復旧

最小読込セット:

1. `docs/guide/linux-listening-lounge-deploy.md`
2. `docs/ops/p0-operations-runbook-2026-07.md`
3. `docs/arch/vikunja-linux-deployment-and-operations-2026-07.md`
4. 実配信・復旧を行う場合だけ `docs/imp/p0-frontend-acceptance-checklist-2026-07-12.html` の定常R06/R07
5. カバレッジHTMLの「運用・安全再配信」行だけ

実装を読む条件:

- 安全な再配信script自体を変更する。
- この場合だけ `infra/deploy/redeploy-p0-frontend.ps1`、`infra/deploy/redeploy-p0-frontend-remote.sh`、`infra/deploy/start-pj-general.sh` と対応テストを読む。ユーザー以外がSSH/sudoを実行しない。

## 設計書化

最小読込セット:

1. `docs/guide/docs-management-rules.md`
2. `docs/guide/implementation-context-reading-guide.md`（この文書）
3. `docs/imp/design-documentation-coverage-assessment-2026-07-13.html`
4. ユーザーへの機能設計レビューを準備する場合だけ `docs/imp/design-documentation-review-summary-2026-07-13.html`
5. 対象行にリンクされた既存正本だけ

実装を読む条件:

- 既存正本だけでは、画面・状態・連携・運用・回帰のいずれかを断定できない。
- 読んだ実装範囲、得られた事実、補完先の正本文書をカバレッジHTMLと `docs/imp/imp-tasks.md` に残す。

## 更新時の判定

- 要件・画面体験: `docs/product/*`
- 状態・操作・API前提: `docs/spec/*`
- 正本・field・event: `docs/data/*`
- 責務分割・連携・実行構成: `docs/arch/*`
- 起動・配信・復旧: `docs/guide/*` または `docs/ops/*`
- 進行、受入、未決: `docs/imp/*`

実装に先行して正本を更新し、同期先にはリンクと状態だけを置く。完了時はカバレッジHTMLの点数・根拠を更新し、`docs/imp/imp-comp.md` と必要なdiaryへ結果を残す。
