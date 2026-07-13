# Thread Line TLロゴ: 選定履歴とベクター実装引継ぎ

## このフォルダの目的

Thread Line Hub / TasksのTLモノグラム選定履歴と、正式PNGアセットの引継ぎである。ここにない大量の試作案は実装基準にしない。

## 選定結果

- TLは、縦長の上品なセリフ系字形を使う。
- TとLを明確に分離する。
- TLの前を横切る大きな斜めの軌道（orbit）を識別要素にする。
- orbitは左下の細い書き出しから始まり、右側・下側で太い帯へ遷移する。
- 形状の主基準は`04-extreme-band-selected.png`である。
- 最終視覚基準は`08-satin-gradient-selected.png`である。
- TはVikunjaアルパカ円背景に近い`#196AFF`、Lは濃いオレンジとする。
- T/Lは浅い立体感を持つ低光沢サテンエナメルとし、Tは青、Lは橙の緩やかな濃淡gradientを使う。
- orbitは銀白を主成分とし、乳白すりガラスと透明クリスタルの中間の光沢を持つホワイトグラス表現とする。
- ラベンダー、紫、ピンク、虹色の帯、暖色またはアクア主体のプリズムは使わない。
- 太いorbitの頂点には、orbitと同じプリズム表現の小さな四芒星状の光芒を置く。
- mark全体は従来案より少し左へ置き、orbitを含む視覚重心を中央へ合わせる。

## 画像一覧

| File | 位置づけ | 次セッションでの扱い |
| --- | --- | --- |
| `assets/01-stripe-tl-origin.png` | 最初に選好された、二本の斜線を持つTL字形 | 字形の緊張感の参考 |
| `assets/02-orbit-direction.png` | orbit導入の初期選好案 | orbitの始点・斜めの動きの参考 |
| `assets/03-orbit-variable-weight.png` | 可変太さのorbit案 | 細い始点と帯への遷移の参考 |
| `assets/04-extreme-band-selected.png` | 太いorbit形状の最有力案 | 形状の主基準 |
| `assets/05-warm-prism-study.png` | 暖色プリズムの試作 | 色は採用しない。プリズムの滑らかさだけ参考 |
| `assets/06-aqua-silver-prism-current.png` | 直近の色・光芒検討 | 次の画像編集の開始点。正式採用は未確定 |
| `assets/07-silver-white-glass-selected.png` | 銀白ホワイトグラス案 | 後続調整の基準履歴 |
| `assets/08-satin-gradient-selected.png` | T/Lへ低光沢サテン立体感と穏やかなgradientを加えた最終案 | 正式原寸PNGの元画像 |
| `assets/thread-line-mark-master.png` | 08と同一内容の1254px正式原寸版 | 実装用の原寸画像 |
| `assets/thread-line-mark-master-256.png` | 原寸版を高品質bicubicで縮小した256px版 | 小表示・実装確認用 |

## 次の実装セッションへの指示

そのまま貼り付けられる文面は`NEXT-SESSION-PROMPT.md`を使う。

1. `assets/thread-line-mark-master.png`を原寸正本にする。
2. 小表示には`assets/thread-line-mark-master-256.png`を使う。
3. SVG化、自動トレース、描き直し、再生成を行わない。
4. Hub / Tasksへ組み込む前に、実表示サイズでPNGの見え方を確認する。

## 保管ルール

- このフォルダの画像は、会話で選好が示された分岐だけを保持する。
- 新しい選好が確定したら、次番号を追加し、このREADMEの「選定結果」と「画像一覧」を更新する。
- 実装用の最終アセットは`apps/web/assets/`およびVikunja forkの配信対象へ別途配置する。ここは選定・引継ぎ用である。
