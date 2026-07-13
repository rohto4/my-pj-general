# 2026-07-12 AI相談UI再設計

## 実施

- `/chat` を1280 x 720で1枚撮影し、会話幅、接続表示、composer到達性を監査した。
- 会話を主役にし、contextを横一列へ圧縮した。
- 初回案では入力、LLM参照、候補化の関係を3段階で表示したが、短高画面では反復説明になるため後続調整で除去した。
- 空会話用の説明と書き出しボタンを追加した。
- `ollama / gemma4:latest` を画面に表示し、実推論とVRAM配置を確認した。
- 左サイドメニューへ常設のサイド相談ボタンを追加した。
- 説明用の大見出しと操作フローを除去し、live contextを薄い帯へ圧縮して残りの画面高を会話へ割り当てた。
- 会話数・thread・接続状態を1行へまとめ、入力欄と送信ボタンを横並びにした。
- `max-height: 900px` / `650px` でAI相談内の文字と余白だけを段階的に縮小した。

## 検証

- `apps/web/check.ps1`: 成功
- 実推論: `OK`
- Ollama load: `size=3281644419`, `size_vram=3281644419`
- 1280 x 720: document overflowなし、live context 26px、message領域533px、composer 102px、入力・送信各52px
- Node回帰: 18件成功
- `git diff --check`: 成功
- サイド相談: 左メニューから起動、drawer 620 x 720px、`aria-hidden=false`

## 継続

- P1のVikunja大幅UX改修へ戻り、共通page guide / empty guideをTDDで実装する。
