# Codex Foundation Repos Comparison

## 目的

`pj-general` の Codex 専用運用土台として、参照・流用候補にした高スター repo のメリットとデメリットを整理する。

比較対象:

1. `aaif-goose/goose`
2. `PrefectHQ/fastmcp`
3. `modelcontextprotocol/servers`
4. `punkpeye/awesome-mcp-servers`

## 比較軸

- この PJ に直接コピーして使えるか
- Codex 専用運用土台として参考になるか
- MCP 実装や外部連携の土台になるか
- ドキュメントや構造が再利用しやすいか
- 将来の拡張余地があるか

## 1. `aaif-goose/goose`

想定役割:

- Codex 向け運用土台の参照元

確認時点の見立て:

- 高スターで実運用感が強い
- `AGENTS.md` を持つ
- `.codex/skills` を持つ
- 複数エージェント向けの構成を併置している

メリット:

- Codex 系の運用構造をそのまま観察できる
- `AGENTS.md` と skill 配置の考え方が実例として強い
- CLI、desktop、API をまたぐ構造なので、将来の発展形が見えやすい
- AAIF 配下に移っていて、今後も agent 標準寄りの知見源になる可能性が高い

デメリット:

- repo 全体は大きく、この PJ に直接コピーして使える部分は限定的
- `.codex/skills` の実体は薄い参照ファイルで、即戦力の `SKILL.md` 集としては使いにくい
- 汎用 agent 基盤なので、この PJ 固有の業務管理サイト開発には広すぎる
- Rust 中心で、MCP 実装土台としてそのまま採るには重い

この PJ との相性:

- 非常に良い。ただし「そのまま使う土台」ではなく「構造参照元」として良い。

採用判断:

- 第一参照元として維持
- `AGENTS.md` / skill 配置 / repo 設計の考え方を参考にする
- 中身を丸ごと取り込むのではなく、必要な方針だけ抽出する

## 2. `PrefectHQ/fastmcp`

想定役割:

- MCP 実装土台
- CLI / skill / ドキュメントの実用品参照元

確認時点の見立て:

- 高スター
- Python 中心
- docs が厚い
- `skills/fastmcp-client-cli` があり、実用 skill をそのまま流用しやすい

メリット:

- MCP を自前実装する時の現実的な第一候補
- `fastmcp-client-cli` のように、すぐ持ち込める skill がある
- docs が整理されていて、今後 Codex に読ませる資料源としても使いやすい
- `server`, `client`, `tools`, `resources`, `prompts` など構成が明瞭
- Python ベースなので、自前サーバや補助ツールを作りやすい

デメリット:

- これは Codex 専用運用土台ではなく、MCP 開発フレームワーク
- repo の目的が広く、PJ初期にはややオーバースペックになる可能性がある
- Horizon など商用導線もあり、全部を鵜呑みにすると構成が肥大化しやすい
- MCP 導入を急ぎすぎると、本来先に決めるべき要件整理より先に技術が走る

この PJ との相性:

- 良い。特に「後で自前の MCP サーバを作る」前提なら強い。

採用判断:

- 実用土台として第一候補
- 既に `fastmcp-client-cli` skill を取り込み済み
- 今後は CLI、client、server のどこを使うかを段階的に決める

## 3. `modelcontextprotocol/servers`

想定役割:

- MCP 参照実装集
- 代表的サーバパターンのカタログ

確認時点の見立て:

- 高スター
- 公式寄りの reference implementations 集
- `filesystem`, `git`, `memory`, `sequentialthinking` など、代表例が揃う

メリット:

- 何を MCP サーバとして切り出すと便利かの発想源になる
- 代表的なサーバ境界を掴むのに向いている
- `filesystem`, `git`, `memory` など、この PJ に近い機能観点がある
- SDK 横断で考える時の基準線になる

デメリット:

- README にある通り、本番向けではなく参照実装
- 直接コピーして使うより、設計の参考にする用途が中心
- この PJ の運用土台そのものにはならない
- セキュリティや threat model は自前で詰め直す必要がある

この PJ との相性:

- 中程度。実装ベースというより、設計観点の補助資料として相性が良い。

採用判断:

- 本番採用元ではなく参照元として維持
- 「どの機能を MCP 化するか」を考える時の土台に使う

## 4. `punkpeye/awesome-mcp-servers`

想定役割:

- MCP エコシステムの巨大索引

確認時点の見立て:

- 非常に高スター
- MCP サーバの一覧 repo
- 直接使う実装土台ではない

メリット:

- 市場全体の見通しを得やすい
- 必要な連携先を探す時の入口として非常に便利
- 後から「この領域に良い MCP サーバはないか」を探す用途に強い

デメリット:

- 土台ではなく索引なので、この PJ にコピーしても即効性は低い
- 玉石混交になりやすく、選定コストがかかる
- セキュリティ、保守状況、品質は別途見極めが必要
- 初期地盤づくり段階では情報量が多すぎる

この PJ との相性:

- 補助資料としては高いが、初期土台としては低い。

採用判断:

- 今回は保留
- 必要になった時だけ探索用に使う

## 総評

役割ごとの第一候補は次の通り。

- Codex 運用構造の参照元: `aaif-goose/goose`
- MCP 実装土台: `PrefectHQ/fastmcp`
- MCP 設計の参照実装: `modelcontextprotocol/servers`
- 探索用索引: `punkpeye/awesome-mcp-servers`

## この PJ での現実的な使い分け

- まず `goose` を見て、Codex 専用運用土台の構造を学ぶ
- `goose` をこの PJ の単独追随先にする
- `fastmcp` は、必要になった時だけ MCP skill やサーバを内製するための参考 repo にとどめる
- `modelcontextprotocol/servers` は、何をどの境界で MCP 化するか考える時に参照する
- `awesome-mcp-servers` は、後で不足機能を探す段階で使う

## 現時点の結論

- 単純さと更新追随性を優先するなら、運用土台の upstream は `goose` 1 本に絞るのがよい
- `fastmcp` は強いが、運用土台として追随すると責務が増える
- したがって、`運用土台は goose を単独追随し、fastmcp は参考 repo として残す` のがこの PJ では最も自然

## 次アクション候補

- `goose` を参考に、この PJ 専用の薄い Codex skill 運用ルールを作る
- `fastmcp` を参考に、将来作る自前 MCP サーバ候補を洗い出す
- 業務管理サイトに必要な作業を、外部 repo 流用で足りるものと、Codex 内製 skill が必要なものに分ける
