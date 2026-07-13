# モダン・リッチ・自由なUI参考 2026-07

調査日: 2026-07-11

## 目的

Hubを一般的なSaaSダッシュボードのカード集合から離し、情報を欠落させずに、本棚、観葉植物、ソファのある書斎で作業するような居心地へ再構成する。

特定サイトの模倣はしない。下記サイト群から、情報階層、文字組み、余白、模様、触感、色、動き、プロダクト表示の長所だけを抽出して組み合わせる。

## 参考URL

### プロダクト・ワークスペース

| # | サイト | URL | 主に見る特徴 |
| --- | --- | --- | --- |
| 1 | Linear | https://linear.app/ | 高密度情報、細い境界、図版番号、操作階層 |
| 2 | Notion | https://www.notion.com/ | 白地と大胆な図版、知識空間の親しみ、手描き感 |
| 3 | Superlist | https://www.superlist.com/ | 強い色面、タスクを重く見せない動きと余白 |
| 4 | Craft | https://www.craft.do/ | 紙・ノートの触感、生活と仕事をつなぐ温度感 |
| 5 | Milanote | https://milanote.com/ | ボード、付箋、素材の並置、視覚的な思考空間 |
| 6 | Cosmos | https://www.cosmos.so/ | 収集物を主役にする静かなグリッドと余白 |
| 7 | Are.na | https://www.are.na/ | 無彩色の知識棚、ブロック間の関係、編集的配置 |
| 8 | Raycast | https://www.raycast.com/ | 機能アイコン、深い色、焦点の明確な操作面 |
| 9 | Arc | https://arc.net/ | 道具感を弱める個性的な色と自由なブラウザ表現 |
| 10 | Figma | https://www.figma.com/ | カラーブロック、図形、共同作業の遊び心 |
| 11 | Framer | https://www.framer.com/ | 大胆なタイポグラフィ、レイヤー、実画面の見せ方 |
| 12 | Pitch | https://pitch.com/ | プレゼン的な画面構成、リズムのある大見出し |
| 13 | Stripe | https://stripe.com/ | 複雑な情報を段階化する図解、色と線のレイヤー |

### クリエイティブ・スタジオ

| # | サイト | URL | 主に見る特徴 |
| --- | --- | --- | --- |
| 14 | Koto | https://koto.com/ | 大胆なブランド色、強い文字、ケースごとの表情 |
| 15 | Instrument | https://www.instrument.com/ | 編集的レイアウト、画像と余白の呼吸、静かな動き |
| 16 | Locomotive | https://locomotive.ca/en | 大型文字、予想外の配置、スクロールの物語性 |
| 17 | Lusion | https://lusion.co/ | 奥行き、空間的なレイヤー、インタラクティブ感 |
| 18 | Basement Studio | https://basement.studio/ | 強い個性、粗さを残す文字と色、規則を外す配置 |
| 19 | Build in Amsterdam | https://www.buildinamsterdam.com/ | 高級感のある余白、素材写真、明快な編集軸 |
| 20 | monopo london | https://monopo.london/ | 文化的な色、軽い不均衡、親しみのある動き |
| 21 | Fable | https://fable.design/ | 物語を作る文字組み、ブランド要素の反復 |
| 22 | aftermodern.lab | https://aftermodernlab.com/ | 厳密なグリッドと意図的な逸脱、出版物の感覚 |
| 23 | Bakoom Studio | https://www.bakoom-studio.com/ | 現代的な視覚言語、キャンペーン的な強い面 |
| 24 | Arithmetic Creative | https://arithmeticcreative.com/ | 人間的な素材、写真、イラスト、感情のある色 |

## 共通して採る設計原則

1. **カードを減らす**: すべてを角丸の箱に入れず、棚板、罫線、色面、余白で領域を分ける。
2. **触感を足す**: 木、紙、布、石、植物を直接画像化せず、低コントラストのCSS模様と色の層で想起させる。
3. **編集的に並べる**: 完全対称のダッシュボードを避け、見出し、注釈、番号、余白で読む順序を作る。
4. **実データを主役にする**: 装飾は情報を隠さず、候補数、種類、優先確認、Tasks概要、判断ログを必ず同じDOMで表示する。
5. **アイコンを案内に使う**: 意味のない絵文字を並べず、入口、確認、Tasks、作業、管理の識別に小さな記号を使う。
6. **不完全さを制御する**: 手描き風や不均衡は装飾層だけに置き、表、フォーム、操作ボタンの整列は崩さない。
7. **角丸を原則禁止する**: panel、summary、table、drawer、filter、list itemは0-2px。丸形はstatus dot、植物の葉、装飾だけに限定する。
8. **狭幅を別構成として扱う**: 添付相当の約1280 CSS pxでは、入口別と候補種類を同じ行・同じ高さにし、右列は下段へ送る。横縮小だけで済ませない。

## 今回の4方向

| ID | 仮称 | 空間 | 色・素材 | レイアウトの特徴 |
| --- | --- | --- | --- | --- |
| `theme-room-01` | Walnut Library | 夜の私設図書室 | ウォルナット、深緑、真鍮、生成紙 | 本棚状の横罫、濃色sidebar、読書灯の色 |
| `theme-room-02` | Sunroom Archive | 朝の温室書斎 | 石灰色、セージ、テラコッタ、明るい木 | 窓の格子、植物影、紙資料の重なり |
| `theme-room-03` | Listening Lounge | 夜のリスニングルーム | 墨色、藍、銅、ウール | 非対称な色面、音響パネル模様、低いソファ感 |
| `theme-room-04` | Nordic Reading Loft | 北欧の屋根裏読書室 | アッシュ、霧灰、コバルト、錆色 | 大きな余白、棚番号、編集的な段組み |

## 採らないもの

- 10px以上の角丸をpanelへ一律適用する。
- すべての項目へ影を付ける。
- 室内写真を背景に敷いて文字を読みにくくする。
- 植物、棚、ソファを装飾するために業務情報を削る。
- 1サイトの色、文字、構成をそのままコピーする。
