# shadcn/ui とガント条件メモ

## 入口 UI

- 入口は自前実装でよい
- UI 基盤候補として `shadcn/ui` を採る方針は自然

根拠:

- 公式サイトで `A set of beautifully designed components that you can customize, extend, and build on.`
- `Open Source. Open Code.`
- GitHub 上でも OSS として公開されている

今回への示唆:

- 入口の体験は自前で作り込みたい
- 既存 PM OSS の画面に寄せるのではなく、必要部品だけ整った基盤を採る方がよい

ソース:

- shadcn/ui: https://ui.shadcn.com/
- GitHub: https://github.com/shadcn-ui/ui

## ガント候補に追加する制約

- Web で閲覧可能
- OSS としてフォークしやすい
- デザインや挙動を後から弄りやすい

## この制約での見え方

### 本線

- OpenProject
- Taiga

### 補助参照

- ProjectLibre
- GanttProject

## ネイティブアプリの利点

- 大規模データでも描画が軽いことがある
- ローカルファイル中心の運用に向く
- オフライン耐性が高い
- MS Project 系の重い PM 表現を真似しやすい

## それでも今回 Web 優先が妥当な理由

- あなたはダッシュボードや横断閲覧を Web 前提で考えている
- ロールで見える範囲を変えるなら、Web の方が運用しやすい
- 入口や AI 分別と同一導線に乗せやすい
- デザイン改変や OSS フォーク前提でも、Web 実装の方が一体化しやすい
