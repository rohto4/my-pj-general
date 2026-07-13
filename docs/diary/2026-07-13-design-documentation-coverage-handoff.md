# 2026-07-13 設計書化カバレッジ handoff

## 完了した断面

- 機能別の設計書カバレッジ正本を`docs/imp/design-documentation-coverage-assessment-2026-07-13.html`として追加した。P0/P1完成度星取表とは別に、クリック編集可能な5段階評価で、正本・実装境界・検証根拠を読むための入口にする。
- 10機能の初期評価は、設計書の充足度として5/5である。P0フロントの実機受入、ユーザー判断、Linux配信の未達はこの表では完了扱いにせず、既存の`p0-p1-completion-assessment-2026-07-12.html`と`p0-frontend-acceptance-checklist-2026-07-12.html`で管理する。
- Hub UI操作契約、Tasks UI契約、複数Projectのproduct/data/spec/arch本文を補完し、実装を横断読込しなくても必要な状態・操作・境界が決定できるようにした。
- `implementation-context-reading-guide.md`と3つのPJ skillに、再利用手順を固定した。
- 横断化できる方法だけは`G:\knowledge-vault\knowledge\dev\design-documentation-coverage-and-minimal-context-reading.md`へ転記した。PJ固有の未達や実機証跡は移さない。

## 次回の再実行手順

1. `AGENTS.md`、`PROJECT.md`、`tech-stack.md`、`README.md`、`docs/imp/user-tasks.md`、`docs/imp/imp-tasks.md`を読む。
2. `docs/guide/implementation-context-reading-guide.md`で作業役割を選び、対象の最小正本文書だけを読む。
3. 対象機能の状態・操作・データ・連携・運用・回帰のどれかが不足する場合だけ、カバレッジHTMLの行を黄色または赤にし、`imp-tasks.md`へ不足を記録する。
4. `audit-design-documentation-coverage`で不足を特定し、`document-implementation-contracts`で正本文書へ補完する。
5. `maintain-design-documentation`で入口、進捗、完了記録、必要なhandoffを同期する。
6. `apps/web/test/design-documentation-coverage.test.mjs`と`git diff --check`を実行する。実データ、Linux配信、再インポートはこの手順の対象外である。

## 検証コマンド

```powershell
& 'C:\Users\unibe\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' --test test/design-documentation-coverage.test.mjs
git diff --check
```

作業ディレクトリは`G:\devwork\pj-general\apps\web`（Node test）および`G:\devwork\pj-general`（diff check）である。
