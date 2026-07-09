# 次セッションの焦点

## 最優先

- ユーザー判断待ちと Codex 側実装待ちを分けた状態を維持する
- P0 画面構成仕様を作る
- ガント MVP 仕様を作る

## Codex が進める具体タスク

1. `docs/spec/screen-structure-p0.md` を作る
2. `docs/spec/gantt-mvp-flow.md` を作る
3. `docs/spec/classification-tag-master.md` を作る
4. `docs/spec/role-and-permission-initial.md` を作る
5. `docs/spec/prompt-template-management.md` を作る
6. `docs/spec/intake-source-adapters.md` を下書きする

## 判断待ち

- `UJ-01`: Slack / knowledge-vault から回収する対象範囲
- `UJ-02`: 回収後の AI 自動分別をどこまで自動確定させるか
- `UJ-03`: 自動確定しない場合、確認待ちキューで何を表示して GO させるか

## 現在のブロッカー

- アプリ実装開始を止めるブロッカーはまだない。
- Slack / knowledge-vault adapter の確定版は `UJ-01` 待ち。
- AI 自動確定の詳細仕様は `UJ-02` 待ち。
- 確認待ちキューの詳細仕様は `UJ-03` 待ち。
