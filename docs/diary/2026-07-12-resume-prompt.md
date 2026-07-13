# 別セッション用・再開プロンプト

以下を新しいセッションの最初のメッセージとして貼り付ける。

```text
このPJ（G:\\devwork\\pj-general）の作業を引き継いでください。

最初に、AGENTS.md、PROJECT.md、tech-stack.md、README.md、docs/imp/user-tasks.md、docs/imp/imp-tasks.mdを実体から読み直してください。続けて、docs/diary/2026-07-12-session-handoff.md、docs/imp/p0-p1-completion-assessment-2026-07-12.html、docs/imp/p0-frontend-completion-tasks-2026-07-12.md、docs/imp/next-goal-p0-frontend-completion-2026-07-12.md、docs/imp/p1-verification-matrix-2026-07-12.mdを読み、要約だけで判断しないでください。

P0のバックエンド・連携契約は完了していますが、P0フロント受入は未完了です。まず次の目標「P0フロント受入完了」を実行してください。順序は、(1)全button/link/form監査、(2)Hub候補・判断フロー受入、(3)Hub↔Vikunja UI責務と状態反映、(4)Vikunja主要画面のguide/empty/action、(5)最新データ構造反映、(6)1280/WQHD/4K縦3分割相当の実画面受入です。P1実機運用はこれらの完了後に再開します。

SSH・sudoが必要な作業は、ユーザーの対話SSH端末で実行してもらう前提にしてください。sudoパスワード、env全文、secret、token、Cookie、秘密鍵内容は表示・保存しないでください。データが0件またはhash不一致でない限り再インポートしないでください。

完成度評価の正本はMarkdownではなく、`docs/imp/p0-p1-completion-assessment-2026-07-12.html`です。HTML星取表の視認性とクリック編集を維持し、数値比較・要確認セル・残タスクを同じHTML内で見分けられる状態にしてください。詳細な根拠と実装タスクは本文・リンク先のdocsへ置いてください。作業開始前に短い実行計画を示し、完了したら実機証拠・未完了・次の目標をdocs/impとdocs/diaryへ同期してください。
```
