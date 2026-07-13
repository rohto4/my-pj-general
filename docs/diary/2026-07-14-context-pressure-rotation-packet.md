# コンテキスト圧迫: 次session再開packet

## 現在の判定

- 直近の実入力: 163,347 / 258,400 token（63.2%）。
- 同一root sessionの圧縮回数: 2回。入力率にかかわらず、運用判定は赤である。
- 当該session用ローカル`visualizations`配置先は0 file / 0 byte。ローカル画像の配置は自動入力されない。
- sessionにある`input_image` 2 blockは、browser screenshotを会話へ表示した結果である。圧縮置換履歴の画像は0 block。

## 次sessionの最小読込

1. `AGENTS.md`
2. `PROJECT.md`
3. `tech-stack.md`
4. `README.md`
5. `docs/imp/user-tasks.md`
6. `docs/imp/imp-tasks.md` のコンテキスト圧迫セッション境界再監査
7. `docs/guide/context-pressure-session-guideline.md`
8. `docs/imp/context-pressure-investigation-2026-07-13.md` の「2026-07-14 セッション境界再監査」節

## 次の作業

ハーネスエンジニアリングを討議する。MCP、Agent Skills、PJ内Harness Profileの責務境界、読込セット、書込ガード、tool出力抑制、session切替を設計対象にする。開始時点ではコード・PJ規約を編集せず、比較と提案を先に出す。

## 継続時の安全境界

- 画像は代表1枚だけを必要時に表示し、全画面比較や画像生成を連続させない。
- tool出力は対象行、件数、失敗行、短い要約に絞る。全文の複数ファイル、全DOM、巨大JSONを会話へ返さない。
- 実データ、Linux、secret、認証情報にはこのハーネス討議の範囲で触れない。
