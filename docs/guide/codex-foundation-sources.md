# Codex Foundation Sources

## 目的

Codex 専用運用土台として、この PJ がどの外部 repo を参照しているかを固定する。

## 単独追随先

- `aaif-goose/goose`

この PJ は、Codex 専用運用土台の upstream として `aaif-goose/goose` を単独で追随する。

## 参考 repo

- `PrefectHQ/fastmcp`
- `modelcontextprotocol/servers`
- `punkpeye/awesome-mcp-servers`

## 使い分け

- `aaif-goose/goose`
  - 参照目的: Codex 向け運用構造、`AGENTS.md`、`.codex/skills` 配置
  - この PJ での扱い: 運用土台の単独追随先

- `PrefectHQ/fastmcp`
  - 参照目的: MCP 実装土台、CLI、skill の実例
  - この PJ での扱い: `fastmcp-client-cli` skill を取り込み済みの参考 repo

- `modelcontextprotocol/servers`
  - 参照目的: 参照サーバ一覧、設計上の典型パターン把握
  - この PJ での扱い: 本番コードではなく参照実装集

- `punkpeye/awesome-mcp-servers`
  - 参照目的: 探索用索引
  - この PJ での扱い: 必要時のみ参照する探索用 repo

## 保存先

- clone 元: `G:\devwork\clone-dir\`
- PJ内コピー:
  - `docs/setting/bootstrap-sources/aaif-goose-goose/`
  - `docs/setting/bootstrap-sources/PrefectHQ-fastmcp/`
  - `docs/setting/bootstrap-sources/modelcontextprotocol-servers/`
  - `.agents/skills/fastmcp-client-cli/`

## 更新ルール

- `goose` だけを upstream として追う。
- `pj-general` 側では `goose` の方針を単純参照し、必要差分だけローカルで足す。
- `fastmcp` と `modelcontextprotocol/servers` は更新を逐次取り込む対象ではなく、必要時に読み直す参考 repo とする。
- 他の clone 済み repo は削除せず、`G:\devwork\clone-dir` に参考用として残す。

## 補足

- スター数の大きさは参照優先度の一因だが、最終判断はこの PJ との適合性を優先する。
- `awesome-mcp-servers` は索引として有力だが、直接コピーして使う土台ではないため単独追随先にはしない。
- 将来的には、流用した土台をそのまま使うだけでなく、この PJ 固有の作業を Codex 用 skill として内製追加する。
