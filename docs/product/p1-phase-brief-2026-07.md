# P1フェーズブリーフ 2026-07

## 目的

P0で成立した候補・判断・Vikunja実行の契約を、日常的に使えて観測できる常設運用へ進める。機能数ではなく、実入口から判断・GO・完了までの運用実績を安全に蓄積することをP1の中心成果とする。

## 成功状態

1. Linux常設環境でHubとListening Lounge版Vikunjaを起動・更新・rollbackできる。
2. 定期workerがsource単位で差分取得し、同じ入力を重複候補にしない。
3. intake -> review -> GO -> task -> mirrorを運用指標で追える。
4. backup / restore / reconcileを定期的に検証できる。
5. Misskey、重複束ね、部分自動確定、Calendarの採否を実データPoCで判断できる。

## スコープ

### P1-A 常設運用基盤

- Hub / Vikunja / Ollamaのhealthと依存縮退
- Hub SQLite、Vikunja DB / files / configのbackup検証
- source run、reconcile、失敗、最終成功時刻の可視化
- Listening Lounge fork `325bc5475` の別tag配信、stable rollback、upstream追随手順
- 候補・判断・GO・execution完了の運用metricsと、Hub復旧後の定期reconcile

### P1-B Vikunja操作体験の再設計

- 全主要ページで「ここは何のページか」「何を入力・操作すると何が起きるか」「次に何をするか」を常時説明する。
- 空状態を空白や事実だけの文言で終わらせず、作成・移動・設定へ進める操作付きguideにする。
- Dashboard / Inbox / List / Table / Kanban / Gantt / task detailの役割を分け、view切替の結果を説明する。
- project単位dashboardと全project横断Hubを混同させない。
- 初回利用者向けの短い導線と、既存利用者を邪魔しない折りたたみ可能なguideを両立する。
- Listening Loungeのsquare surface、銅色action、棚・ラベル・余白の読順を維持する。

### P1-B 定期入口同期

- `workers/sync` のoneshot化
- systemd timerで6時間ごと、`Persistent=true`、排他実行
- knowledge-vaultを第1adapter、Slack payloadを第2adapter
- source cursor / dedupe key / run resultを永続化

### P1-C 判断支援PoC

- 類似候補の提示。自動統合はしない。
- source / kind / confidence / missing /編集差分 / GO率を記録する。
- 部分自動確定はdry-runだけ行い、ユーザーGOを迂回しない。

### P1-D 外部入口・予定PoC

- Misskeyはread-onlyの最小権限で方式比較する。
- Calendarはユーザー操作による一方向event作成だけをPoCする。

## 非スコープ

- LLMやworkerによる自律GO
- Calendar双方向同期
- 複数組織向け本番権限
- PostgreSQL / Redis / BullMQの理由なき先行導入
- Next.js等への全面移行とP1機能の同時実施
- Vikunja unstable APIへの追随
- マルチエージェント開発基盤

## 優先順位と依存

```text
P1-A 運用
  -> P1-B Vikunja UX再設計・fork配信
  -> P1-C 定期worker
    -> 実運用データ蓄積
      -> P1-C 重複・自動確定PoC
      -> P1-D Misskey / Calendar PoC
        -> PostgreSQL / auth / queue再判定
```

## データ変更

P1初期はSQLiteを維持し、次の論理テーブルを追加候補とする。

- `source_sync_runs`: source、開始/終了、cursor、取得/作成/skip件数、state、error
- `source_items`: source + external id / content hashによるRaw lineage
- `candidate_similarity`: 比較元・候補・score・判定。自動mergeしない
- `calendar_links`: candidate / taskと外部event id、idempotency、最終同期状態

PostgreSQL移行時もcandidate ID、decision、execution link、source lineageを維持する。移行前後の件数・hash・外部IDを照合し、SQLiteを直ちに削除しない。

## 導入ゲート

### PostgreSQL

次のどれかが発生した場合に実装へ進める。

- Webとworkerの同時書込みでlock待ち・失敗が観測される。
- 認証・複数利用者・組織境界が必要になる。
- candidate / source itemが1万件規模となり、検索・集計で問題が出る。
- queue / outboxをDB transactionと一体化する必要が出る。

### 部分自動確定

- 対象segmentごとに十分な判断実績がある。
- missingなし、外部副作用なし、取消可能な対象に限定する。
- dry-runで誤確定候補が0件である。
- 最終的な有効化はユーザー判断とする。

### 認証・権限

二人目または外部協力者へ公開する前に必須化する。それまでは設計とPoCに留める。

## P1受入条件

- timerを連続2回実行しても同一source itemからcandidateが増えない。
- 入口ごとの失敗が他入口を止めず、最終成功・失敗理由を画面または運用出力で確認できる。
- Hub停止後もVikunja task実行を継続でき、復旧後reconcileで一致する。
- backupから別場所へ復元し、件数・主要hash・外部linkを照合できる。
- custom Vikunjaからstableへデータ損失なくrollbackできる。
- Dashboard / Inbox / List / Table / Kanban / Gantt / task detailでページの役割と主要操作の結果を説明できる。
- task 0件、bucket 0件、日付対象0件でも、空白ではなく次の操作を持つempty guideが表示される。
- 1280px / 1920pxでguideが主操作を覆わず、document横overflowと2px超の構造角丸がない。
- PoCは採用 / 保留 / 対象外と根拠を記録し、本実装へ暗黙移行しない。

候補比較の根拠は `docs/candi-ref/p1-candidate-evaluation-2026-07.md`、実装単位は `docs/imp/p1-implementation-tasks-2026-07.md` を正本とする。
