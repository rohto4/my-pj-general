# 次の目標: P1実機運用仕上げと最初の実運用データ巡回

> 2026-07-12再評価により、P0フロント受入が先行するため一時保留。P0追加タスク完了後に再開する。

## 目的

P0を再オープンせず、P1に残る実機・復旧・運用データの証跡を揃え、P1を完了判定できる状態へ進める。

## 実行順

1. LinuxでVikunja custom imageを別tagへ切り替え、UI / health / task件数を確認する。
2. stable imageへrollbackし、task ID・execution link・件数が一致することを確認する。
3. systemdのsource sync / backup / reconcileを登録し、2回分のjournalと冪等結果を保存する。
4. Hubだけを停止してVikunjaを継続させ、Hub復旧後のreconcile一致を確認する。
5. 外部mirrorを設定できる場合は設定し、できない場合は保留理由をP1文書へ記録する。
6. 候補のedit → GO / reject / archive → execution完了を最低1巡回し、observabilityのmetricsを更新する。
7. Misskey・類似束ね・部分自動確定・Calendar・PostgreSQL・認証を、実データに基づき採用 / 保留 / 対象外に判定する。
8. P1監査、verification matrix、実装タスク、next-session focus、diaryを実体に合わせて同期する。

## 完了条件

- custom→stable rollback後にデータ差分がない。
- timer 2回分のjournalで重複登録・相互汚染がない。
- Hub停止→復旧→reconcileの実機証跡がある。
- 候補ライフサイクル1巡回のmetricsが確認できる。
- P1各PoCが採用・保留・対象外のいずれかに決まる。
- P1完了監査の未証明欄が、実体または明示的保留理由で埋まる。

## 制約

- P0の完了判定を取り消さない。新しい回帰が見つかった場合だけP0タスクへ戻す。
- sudoパスワードをチャットへ書かない。systemd登録はユーザーのSSH端末で実行してもらう。
- secret、token、Cookie、env全文、秘密鍵の内容を表示・保存しない。
- PostgreSQL、認証、queueの本実装は導入ゲートを満たすまで先行しない。
