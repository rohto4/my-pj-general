# Knowledge・prompt candidate register

追記基準、3段階の役割分担、状態遷移は `G:\devwork\tool-set\docs\ops\knowledge-candidate-register-policy.md` に従う。

作業中に横断知識または繰り返す依頼の候補が生まれたときだけ、下の最小形式で追記する。これは監査が必要な根拠だけを再現するための証拠パケットであり、記事本文やprompt本文、生ログをこのファイルに書かない。

## 最小記入テンプレート

```md
## K-YYYYMMDD-NNN
- 事象: 決定・比較・失敗・検証・成果・依頼のうち、今回起きたこと
- 種別: decision | comparison | failure | reusable-pattern | milestone | handoff
- 仕分け: knowledge | prompt | undecided
- 要約:
- 根拠: 相対パスまたはPJ内の正本パス
- 確認範囲: 根拠の見出し、検証名、または読む最小の節
- きっかけ: 再利用・判断・復元価値、または反復する依頼である理由
- 状態: candidate
```

作業中は候補を残してよいが、実記録に進める前に完了・判断・検証の直接根拠を同じ候補へ追記する。

## K-20260717-001

- 事象: 共通候補提案promptをv2から圧縮したv3へ更新し、Ollama互換JSON出力の途中終了を出力上限調整で解消した。
- 種別: reusable-pattern
- 仕分け: knowledge
- 要約: 共通promptは禁止境界を維持して短縮し、構造化JSONが長い場合はvalidatorを弱めず出力token上限とfake HTTP・実dry-runで完結性を確認する。
- 根拠: docs/imp/imp-comp.md
- 確認範囲: 「2026-07-16 共通候補提案 prompt v3 圧縮と完全JSON回帰」
- きっかけ: 複数入口で同じlocal LLMの構造化出力を扱うPJに、prompt短縮とtruncate診断の再利用価値がある。
- 状態: candidate
