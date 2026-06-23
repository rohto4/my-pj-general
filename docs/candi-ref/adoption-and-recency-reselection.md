# 利用者数 / 新しさ重視での再選定メモ

## 前提

- このメモは `機能適合` よりも `利用者規模` と `新しさ` を強く見る
- 特に `2026-01-01` 以降の動きがあるかを重視する
- ただし、OSS 本線として残すには最低限 `公開コード` と `継続更新` が必要

## Backlog について

- `Backlog` は OSS ではない
- 公式サイトでは SaaS プロダクトとして案内されており、価格ページ、AI、各種連携、Enterprise バンドルが前面に出ている
- 公式に `TRUSTED BY OVER 4 MILLION USERS WORLDWIDE` とある

今回への示唆:

- OSS ではないが、`利用者数` と `新しさ` の観点では非常に強い比較対象
- もし `OSS に限定しない` なら本線候補に即入る

ソース:

- https://nulab.com/backlog/

## OSS 本線を利用者数 / 新しさで並べ直した場合

### 1. Plane

- GitHub Star: `52.6k`
- GitHub Fork: `4.7k`
- 公式 README 上で `Pages`、`AI capabilities`、`Analytics` を確認できる
- 現代的な PM OSS として勢いが強い

評価:

- `新しさ`: 高い
- `公開で見える勢い`: 高い
- `AI 時代との親和性`: 高い
- 弱点:
  - 実利用者数の公開値は Backlog ほど明確ではない
  - ガント主軸ではなく、PJ 管理全体と入口寄り

### 2. OpenProject

- GitHub Star: `15.4k`
- GitHub Fork: `3.3k`
- OpenProject は 2025 年時点でも大規模採用事例が見え、公式・第三者レビューも継続
- G2 レビューは `25件` と少ないが、2025 年レビューがある

評価:

- `新しさ`: 中
- `実運用の厚み`: 高い
- `ガント / 横断管理`: 強い
- `AI 時代との親和性`: 中

### 3. Redmine

- GitHub Star: `6k`
- GitHub Fork: `2.4k`
- G2 レビューは `257件`
- 直近レビュー確認日: `2026-04-10`, `2026-03-30`, `2026-03-10`
- 古いが、依然として実利用の厚みが強い

評価:

- `新しさ`: 低〜中
- `利用者層の厚み`: 高い
- `古典的な安心感`: 高い
- `AI 時代との親和性`: 低〜中

### 4. Taiga

- GitHub Star は今回開いた repo では小さく見えるが、Taiga は OSS PM の古典候補として知名度が高い
- 2025-10-10 時点のリリース情報が確認できる

評価:

- `新しさ`: 中
- `利用者の厚み`: 中
- `アジャイル課題管理`: 強い
- `AI 時代との親和性`: 中以下

### 5. Tuleap

- G2 レビュー `20件`
- 直近レビューは `2026-01-14`, `2025-12-24`, `2025-12-01`
- Enterprise / ALM 寄りで、一般 OSS の勢い指標より導入先の濃さが価値

評価:

- `新しさ`: 中
- `公開人気`: 中以下
- `重い組織導入`: 高い
- `AI 時代との親和性`: 中以下

### 6. ProjectLibre

- ProjectLibre Desktop のダウンロード数は `7,600,000`
- 2025-04-28 リリース
- ただし desktop 主体

評価:

- `利用者規模`: 高い
- `新しさ`: 中
- `今回の Web 条件`: 弱い

## 2026-01 以降に出てきた新規寄り候補

### Workstream

- GitHub Star: `7`
- 2026-04 頃に公開されたローカル開発者向けダッシュボード OSS
- PR、tasks、calendar、AI を 1 画面で扱う

評価:

- 発想はかなり近い
- ただし、現時点では `新しいが、利用者数の裏付けが弱すぎる`
- 本線候補ではなく、`設計発想の参考`

ソース:

- https://github.com/happybhati/workstream

## 再選定の結論

### OSS 本線を 3 件に絞るなら

1. `OpenProject`
2. `Plane`
3. `Taiga`

理由:

- `OpenProject`: ガントと横断管理で最も強い
- `Plane`: AI 時代の勢いと modern OSS として最も強い
- `Taiga`: 利用者規模では Plane / OpenProject に劣るが、現代OSSとして比較対象に残しやすい

### 条件付きで残す

- `Taiga`: アジャイル寄り比較対象
- `Tuleap`: 権限 / traceability / ALM 比較対象
- `ProjectLibre`: ダウンロード規模は強いが desktop 主体

### OSS 以外も含めるなら

- `Backlog` は本線候補に入る
- 4 million users と 2026 年時点の AI / integration 訴求は無視しにくい

## 今回の実務判断

- `OSS に限定` して `利用者数 / 新しさ` で本線を組み直すなら:
  - `OpenProject`
  - `Plane`
  - `Taiga`

- `AI 時代に入ってから新しく出たものも評価` という観点では:
  - `Workstream` のような新規 OSS は発想は面白い
  - ただし、まだ本線候補にするには早い

## 現時点の温度感メモ

- `Plane` はかなり熱い候補
- 理由は、単なる PM OSS ではなく `modern OSS`, `AI capabilities`, `Pages`, `modern project management` の文脈が揃っているため
- 入口を自前実装にする前提でも、`周辺の情報設計`, `AI 補助の考え方`, `現代的な体験設計` の主参照先として価値が高い
- `Redmine` は古さを理由に本線候補から外す

## ソース

- Backlog: https://nulab.com/backlog/
- Plane GitHub: https://github.com/makeplane/plane
- OpenProject GitHub: https://github.com/opf/openproject
- Redmine GitHub: https://github.com/redmine/redmine
- Taiga: https://taiga.io/
- Taiga info: https://en.wikipedia.org/wiki/Taiga_%28project_management%29
- ProjectLibre: https://en.wikipedia.org/wiki/ProjectLibre
- Workstream GitHub: https://github.com/happybhati/workstream
