# UI agent skill 調査メモ

作成日: 2026-07-09

## 目的

P0 薄く実装 1 版の見た目改善を、WQHD スクリーンショット反復と Agent Skills で再現しやすくする。

## 確認した情報源

| 情報源 | 用途 | 確認した内容 | URL |
| --- | --- | --- | --- |
| Anthropic `skills` repository | 公開 Agent Skills の実例 | skills は `SKILL.md` と任意の `scripts` / `references` / `assets` で構成され、creative/design、development/testing、document 系の例がある | https://github.com/anthropics/skills |
| Anthropic `skills/skills` directory | UI 関連候補の棚卸し | `frontend-design`, `webapp-testing`, `web-artifacts-builder`, `theme-factory`, `canvas-design` を確認 | https://github.com/anthropics/skills/tree/main/skills |
| Agent Skills overview | 形式と運用の確認 | skill は軽量フォルダで、name/description による discovery、必要時の `SKILL.md` 読み込み、任意リソース実行という progressive disclosure | https://agentskills.io/ |
| `frontend-design` | 見た目改善の参照 | 汎用テンプレート臭を避け、対象固有の視覚方向・タイポグラフィ・レイアウトを決める方針が有用 | https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md |
| `webapp-testing` | スクショ検証の参照 | Playwright / ブラウザで local web app を開き、network idle 後にスクショや DOM を確認する流れが有用 | https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md |
| `web-artifacts-builder` | shadcn/Tailwind 参照 | React / Tailwind / shadcn/ui を使う複雑な UI artifact の考え方と、AI っぽい過剰装飾を避ける注意が有用 | https://raw.githubusercontent.com/anthropics/skills/main/skills/web-artifacts-builder/SKILL.md |
| `theme-factory` | テーマ設計の参照 | 配色、フォント、視覚 identity をテーマとして揃える考え方が有用 | https://raw.githubusercontent.com/anthropics/skills/main/skills/theme-factory/SKILL.md |

## このPJへ追加した派生 skill

| skill | 目的 | 参照した考え方 |
| --- | --- | --- |
| `.agents/skills/wqhd-ui-screenshot-loop/SKILL.md` | 2560x1440 の実スクショを見ながら UI を反復修正する | `webapp-testing` の rendered-state-first / screenshot-first |
| `.agents/skills/operations-dashboard-polish/SKILL.md` | 業務ツールとしての密度、指標、キュー、操作ボタンを整える | `frontend-design`, `theme-factory`, このPJの frontend guidance |
| `.agents/skills/agent-skill-source-review/SKILL.md` | 外部 skill を調べ、安全にPJローカルへ派生させる | Agent Skills overview と Anthropic repo の構成 |

## 判断

今回は外部 skill の全文コピーではなく、参照元を記録したうえで PJ 固有の短い派生 skill を作る。理由は次の通り。

- UI改善では、このPJの「業務ツール」「日本語表示」「確認待ちキュー」固有の判断が重要。
- 外部 skill は汎用性が高い一方、このPJの docs 更新ルールや WQHD 固定検証までは持っていない。
- license と将来更新差分を追う負担を小さくするため、workflow pattern だけを取り込む。
