# P1 認証 resource-action matrix

P1では認証基盤を先行導入せず、Better Auth導入前に「誰が、どの正本に、どの操作を行えるか」を固定する。現在は単一利用者のため、この文書は実装済み権限ではなく、公開前に認可評価へ変換する設計正本である。

## 判定値

| 値 | 意味 |
|---|---|
| `allow` | 操作を実行できる |
| `read` | 閲覧だけできる |
| `deny` | UI/APIともに拒否する |
| `confirm` | ユーザーの明示確認を要求する。AIやworkerだけでは実行しない |
| `design` | 役割・組織導入時に再判定する |

## Resource-action matrix

| resource | view | create | edit | approve / GO | reject / archive | sync / reconcile | manage |
|---|---|---|---|---|---|---|---|
| intake source / source lineage | allow | allow | read | deny | deny | confirm | design |
| candidate | allow | allow | allow | confirm | confirm | deny | design |
| decision history | allow | deny | deny | deny | deny | deny | design |
| execution link | allow | confirm | deny | confirm | deny | confirm | design |
| mirrored execution state | allow | deny | deny | deny | deny | allow | design |
| chat thread / message | allow | allow | deny | deny | deny | deny | design |
| AI suggestion | allow | allow | allow | confirm | confirm | deny | design |
| observability / source runs | allow | deny | deny | deny | deny | allow | allow |
| backup manifest / restore evidence | read | deny | deny | deny | deny | deny | allow |
| admin settings / integration secret reference | read | deny | confirm | deny | deny | deny | allow |
| Vikunja task | read | confirm | read | confirm | deny | confirm | design |

## 初期ロール

| role | 適用範囲 | 原則 |
|---|---|---|
| `owner` | Hub / Vikunja / worker / backup | 全画面を閲覧できる。候補のGO、不要、archive、外部task作成、restore、設定変更は明示確認を経て実行する |
| `collaborator` | 割り当てられた候補・実行task | 閲覧と編集は許可するが、GO、外部task作成、backup/restore、secret、integration設定は拒否する |
| `observer` | 監査・共有画面 | observability、decision、task状態をread-onlyで閲覧する。候補編集や外部同期は拒否する |
| `automation` | worker / reconcile / backup | 許可されたscopeの同期と証跡記録だけを行う。GO、候補の自動確定、secret表示、権限変更は拒否する |

## API評価の境界

1. UIの非表示だけを認証境界にしない。`resource`, `action`, `actor`, `scope`, `candidateId`をAPI側で評価する。
2. `confirm`は、ユーザー操作の監査記録（actor、時刻、対象ID、入力要約、結果）を作ってから外部書き込みへ進む。
3. workerはsourceごとのscopeを持ち、knowledge-vault / Slack / Vikunjaを横断して候補を確定しない。
4. Vikunjaのtask状態は実行正本だが、Hubのcandidateやdecisionを直接上書きする権限は持たない。Hubへの反映はWebhook / reconcileの許可されたmirror操作に限定する。
5. backup / restoreは`owner`の運用操作に限定し、restore前後の件数・hash・external IDを比較して証跡を残す。

## P1での再判定ゲート

- 二人目の利用者、または外部協力者が実際にログインする。
- candidate編集とGOが同時に発生し、競合・監査上の不整合が観測される。
- sourceごとの共有範囲（個人、チーム、公開）が必要になる。
- `automation`が候補作成を越えて外部サービスへ書き込む必要が生じる。

上記のいずれかを満たすまでは、P1の認証PoCはこのmatrixとAPI契約の設計継続に留め、Better Authの本番導入はP2候補とする。

実装開始前のrole別API検証、確認なしの書込み拒否、実データ公開前の受入・復旧境界は `docs/spec/p1-start-gate-acceptance-contract-2026-07.md` を正本とする。
