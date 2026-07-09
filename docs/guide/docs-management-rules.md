# docs 管理・更新ポリシー

## 目的

この文書は、`docs` 配下の文書関係、正本、同期先、更新漏れが起きやすい状況を定義する。

大原則は、正本を1つ決め、他文書には要約、リンク、状態だけを同期することである。

図で把握したい場合は `docs/guide/docs-management-matrix-result-diagram.md` を参照する。

この文書は、PJ 内 docs に対する `docs-update-policy` として扱う。
`pj-general` 固有の一時メモではなく、開発系PJへ引き継ぐ共通運用テンプレートである。
新PJへ移す場合は、PJ名、目的、ディレクトリ実体だけをそのPJ向けに調整し、更新判断表と正本分離の考え方は維持する。
横断ナレッジへの記録判断は `G:\knowledge-vault\knowledge-vault-write-policy.md` を正本にする。

## 更新判断の基本

- 仕様更新時だけでなく、タスク整理、タスク進捗、判断待ち発生、判断待ち解消、完了、handoff 作成の各タイミングで、PJ docs と knowledge-vault の更新要否を評価する。
- 評価は「全ファイルを更新する」意味ではない。影響がある正本と同期先だけを更新する。
- PJ 固有の進行状態は PJ 内 docs を正本にしつつ、knowledge-vault へは中央 policy に従って、再利用できる知見、判断経緯、運用ルール、失敗知、復元価値のある作業記録を既存カテゴリへ反映する。
- 判断待ち、実装待ち、完了記録は `docs/imp/` に集約し、仕様・設計本文に長く残さない。
- `docs/diary/` は handoff と復元用であり、最新状態の正本にしない。

## 文書関係マトリクス

| 領域 | 正本 | 主な同期先 | 更新トリガー | 更新漏れが起きる状況 |
| --- | --- | --- | --- | --- |
| PJ 実行ルール | `AGENTS.md` | `PROJECT.md`, `docs/guide/*`, `docs/README.md` | エージェントの必須行動、読み込み順、禁止事項を変える | `docs/guide` だけ直して、実行時に読む `AGENTS.md` が古い |
| PJ 目的・構造・恒久判断 | `PROJECT.md` | `README.md`, `docs/README.md`, 関連する `docs/arch/*` / `docs/spec/*` | PJ の目的、スコープ、作業入口、正本関係、恒久的な構造、採用済み重要判断を変える | PROJECT にタスク、履歴、参照元ログが混ざる、または入口ファイルだけ増え PROJECT の作業入口が古い |
| 毎チャット起動 | `AGENTS.md` | `PROJECT.md`, `docs/imp/next-session-focus.md`, `docs/diary/*` | 起動時に毎回読むべき共通前提や現状把握の読み先を変える | セッション固有情報を AGENTS.md に混ぜる、または diary だけが最新状態になる |
| 技術スタック | `tech-stack.md` | `docs/arch/*`, `PROJECT.md` | 採用候補、代替候補、実務コマンドを変える | arch の比較結果だけ更新し、tech-stack の第一候補が古い |
| docs 置き場所 | `docs/guide/docs-management-rules.md` | `docs/README.md`, `AGENTS.md`, `PROJECT.md` | docs の責務、正本関係、同期ルールを変える | README の一覧と実際の運用ルールがずれる |
| プロダクト体験 | `docs/product/*` | `docs/spec/*`, `docs/data/*`, `docs/imp/*` | ユースケース、画面方針、体験フローを変える | 画面や体験の変更が、仕様・データ・タスクに反映されない |
| 確定仕様 | `docs/spec/*` | `docs/data/*`, `docs/product/*`, `docs/imp/*` | 状態、操作、API 前提、外部連携仕様を変える | 仕様本文に未決事項や実装TODOが残る |
| データモデル | `docs/data/*` | `docs/spec/*`, `docs/arch/*` | object、event、状態、同期単位を変える | spec のフィールド追加が data 側に反映されない |
| アーキテクチャ | `docs/arch/*` | `tech-stack.md`, `docs/spec/*` | 責務分割、採用理由、境界を変える | 技術比較の判断が tech-stack に同期されない |
| 組織・権限 | `docs/org/*` | `docs/spec/*`, `docs/product/*` | ロール、権限、見せる情報範囲を変える | 画面仕様だけ変わり、権限前提が古い |
| 運用手順 | `docs/guide/*`, `docs/ops/*` | `AGENTS.md`, `PROJECT.md` | 採用済み手順、保守、監査、日次運用を変える | 採用済み手順なのに guide/ops ではなく diary に残る |
| 候補・比較 | `docs/candi-ref/*` | `docs/arch/*`, `tech-stack.md`, `docs/imp/*` | OSS 候補、比較表、未採用理由を変える | 候補比較が採用判断に昇格したのに arch/tech-stack に移らない |
| 進行管理 | `docs/imp/*` | `docs/diary/*` | 判断待ち、実装待ち、完了記録、次回焦点を変える | spec/product/data に TODO が散り、imp から追えない |
| セッション記録 | `docs/diary/*` | `docs/imp/*` | 長い会話の引き継ぎ、当日成果、次回読み順を残す | diary にだけ最新状態があり、imp のタスク一覧が古い |
| 初期設定・流用元 | `docs/setting/*` | `docs/guide/*`, `PROJECT.md` | テンプレート、参照元、取り込み元を変える | 流用元の記録を直接編集し、採用済みルールと混ざる |
| 横断ナレッジ | `G:\knowledge-vault` | `AGENTS.md`, `docs/imp/imp-comp.md` | 再利用できる知見、判断経緯、復元価値のある作業記録を保存する | PJ内正本へ置くべき未完TODOや一時メモを knowledge-vault だけに書く |

## タイミング別更新判断表

| タイミング | 必ず確認するPJ docs | 更新する条件 | knowledge-vault 評価 |
| --- | --- | --- | --- |
| タスクをまとめた | `docs/imp/imp-tasks.md`, `docs/imp/user-tasks.md`, `docs/imp/next-session-focus.md` | 新規TODO、優先度、担当境界、次回焦点が変わる | タスク整理方法や運用原則として記録価値がある場合は評価 |
| タスクが進んだ | `docs/imp/imp-tasks.md`, `docs/imp/imp-comp.md` | 着手、分割、保留、完了、不要化が発生する | 再利用できる手順、失敗回避、検証方法が得られた場合は評価 |
| ユーザー判断待ちが発生した | `docs/imp/user-judge.md`, `docs/imp/user-tasks.md` | ユーザーの判断、確認、実機操作が必要になる | 判断軸、未決理由、後続影響に記録価値がある場合は評価 |
| ユーザー判断待ちが解消した | `docs/imp/user-judge.md`, 該当する `docs/product/*`, `docs/spec/*`, `docs/data/*`, `docs/arch/*` | 判断済みに変わり、仕様・設計・比較へ反映できる | 採用理由、却下理由、再評価条件が得られた場合は評価 |
| 仕様・設計が変わった | 該当する `docs/product/*`, `docs/spec/*`, `docs/data/*`, `docs/arch/*`, `docs/org/*` | 要件、状態、操作、データ、権限、構成、境界が変わる | 設計原則、責務分割、判断基準が得られた場合は評価 |
| 候補比較が判断へ昇格した | `docs/candi-ref/*`, `docs/arch/*`, `tech-stack.md`, `docs/imp/imp-comp.md` | 採用、不採用、保留、再評価条件が決まる | 比較軸、根拠、選定原則が得られた場合は評価 |
| 運用ルールを変えた | `AGENTS.md`, `PROJECT.md`, `docs/guide/*`, `docs/README.md` | エージェント動作、読み込み順、docs配置、更新ルール、正本責務が変わる | 複数PJへ展開できる運用ルールなら評価 |
| 重要文書を追加・移動した | `PROJECT.md`, `README.md`, `docs/README.md`, 関連する `docs/guide/*` | 新しい正本、入口、図、テンプレート、ガイドを作る | 汎用テンプレート化できる場合は評価 |
| コンテキスト圧縮・セッション移動から再開した | `AGENTS.md`, `PROJECT.md`, `tech-stack.md`, `README.md`, `docs/imp/*`, 必要なら `docs/diary/*` | 圧縮後要約、handoff、セッション移動を検知した直後。通常回答や作業継続の前に読む | 再開手順や圧縮復帰の失敗回避として再利用できる場合は評価 |
| セッション要約・handoffを作る | `docs/diary/*`, `docs/imp/*`, `docs/imp/next-session-focus.md` | 次回復元が必要、または長時間作業の状態を残す | 作業経緯を vault 側で復元する価値がある場合は評価 |
| 外部知識として保存した | `docs/imp/imp-comp.md`, 必要なら `docs/diary/*` | knowledge-vault へ反映した事実をPJ側にも残す | `G:\knowledge-vault\knowledge-vault-write-policy.md` に従う |

## knowledge-vault 判定ゲート

PJ 作業中に以下のどれかに該当する場合は、`G:\knowledge-vault\knowledge-vault-write-policy.md` を読んで反映先を判断する。

- 複数PJで再利用できる判断原則、比較軸、運用ルールが固まった。
- 技術選定、OSS選定、設計境界、検証手順などの再利用可能な知見が得られた。
- 失敗回避、更新漏れ防止、handoff、agent運用などの横断ノウハウが得られた。
- 後から別PJで想起する価値がある作業記録や判断理由がある。
- タスク整理、進捗、判断待ち、判断解消、完了などの過程で、後から復元・比較・再利用できる記録が生まれた。

以下は原則として knowledge-vault へ反映しない。

- PJ 固有の未完TODO、進捗、作業途中メモ。
- 一度きりの操作ログや、このPJのファイル差分だけの記録。
- 仕様本文や比較表の全文コピー。
- 根拠未確認の推測。

## 更新漏れが発生しやすいパターン

| パターン | 典型例 | 防止ルール |
| --- | --- | --- |
| 判断待ちと仕様が混ざる | `docs/spec/*` に「後でユーザー確認」と残る | ユーザー判断待ちは `docs/imp/user-judge.md` へ移す |
| 次アクションが設計書に残る | `docs/product/*` に「次に作る」が散る | Codex 作業は `docs/imp/imp-tasks.md` へ移す |
| diary が最新正本になる | セッション要約だけが最新で、imp が古い | diary 作成時に `docs/imp/*` の状態を合わせる |
| 比較結果が採用判断へ昇格しない | `docs/candi-ref/*` に候補比較だけ残る | 採用・不採用判断は `docs/arch/*` または `tech-stack.md` へ反映する |
| 入口ファイルが古くなる | 新しい正本を作ったが README / PROJECT にない | 新規の重要文書を作ったら入口一覧を更新する |
| 同じルールを複数箇所に長文コピーする | `AGENTS.md` と guide に同じ詳細がある | `AGENTS.md` は実行ルール、詳細は guide に集約する |
| PROJECT が履歴置き場になる | `PROJECT.md` に今回の到達目標、次走テーマ、参照元一覧、作業ログが残る | PROJECT は PJ 固有の目的、構造、正本関係、恒久判断だけにし、タスクは `docs/imp/*`、履歴は `docs/diary/*`、参照元は `docs/candi-ref/*` / `docs/setting/*` へ移す |
| 圧縮後要約だけで再開する | コンテキスト圧縮後に、要約を読んだだけで通常回答や作業継続に入る | 圧縮、handoff、セッション移動を検知したら、最初の通常回答より前に `AGENTS.md` から読み込み順どおり再読み込みする |

## 編集手順

1. 発生した変更のタイミングを、上の「タイミング別更新判断表」で判定する。
2. 変更内容の正本を決める。
3. 正本を更新する。
4. 同期先に、要約、リンク、状態だけを反映する。
5. 未決事項は `docs/imp/user-judge.md`、Codex 作業は `docs/imp/imp-tasks.md`、ユーザー作業は `docs/imp/user-tasks.md` に移す。
6. 完了した作業は `docs/imp/imp-comp.md` に追記する。
7. 次回引き継ぎが必要な場合だけ `docs/diary/` に要約する。
8. knowledge-vault への反映要否を評価し、記録対象がある場合は `G:\knowledge-vault\knowledge-vault-write-policy.md` に従って反映する。

## セッション終了時チェック

長い作業、handoff 作成前、または最終報告前には、必要に応じて次を確認する。

- `docs/imp/imp-tasks.md` に残すべき作業が反映されているか。
- `docs/imp/user-judge.md` / `docs/imp/user-tasks.md` にユーザー待ちが反映されているか。
- 完了した作業が `docs/imp/imp-comp.md` に記録されているか。
- `docs/diary/*` だけが最新状態になっていないか。
- `docs/spec/*`、`docs/product/*`、`docs/data/*`、`docs/arch/*` に不要なTODOや判断待ちが残っていないか。
- `docs/candi-ref/*` の比較結果が採用判断へ昇格した場合、`docs/arch/*` または `tech-stack.md` に反映されているか。
- 新しい重要文書を作った場合、`PROJECT.md`、`README.md`、`docs/README.md` の入口が必要に応じて更新されているか。
- 知見、判断経緯、作業記録について、knowledge-vault への反映要否を評価したか。

## 新規文書を作る基準

- 既存文書に入れると責務が混ざる場合は新規作成する。
- 1文書は1責務にする。
- 一時的な検討は `docs/imp/` または `docs/diary/` に置き、確定したら該当正本へ移す。
- 採用済み手順になったものは `docs/guide/` へ移す。

## 文書種別ごとの禁止事項

| 文書種別 | 置かないもの |
| --- | --- |
| `AGENTS.md` | 長い分析表、セッション固有メモ |
| `PROJECT.md` | タスク一覧、進捗、次走テーマ、セッション履歴、handoff、判断材料の生ログ、参照元一覧、調査メモ、一時的なTODO |
| `docs/spec/*` | 実装待ち一覧、ユーザー質問一覧 |
| `docs/product/*` | DB 詳細、インフラ詳細 |
| `docs/data/*` | 画面コピー、運用TODO |
| `docs/candi-ref/*` | 採用済みルールの正本 |
| `docs/imp/*` | 確定仕様の長文本文 |
| `docs/diary/*` | 恒久ルールの正本 |
| `docs/setting/*` | 現行運用ルールの正本 |

## 新PJへ引き継ぐ最小ルールセット

新しいPJでこの運用を継承する場合は、最低限次を引き継ぐ。
初期化プロンプトで `AGENTS.md`、`PROJECT.md`、AI設定関連ファイル、ディレクトリ構造を `pj-general` から引用するよう指示された場合、この一覧を引き継ぎ対象として扱う。

- `AGENTS.md`: 実行時の短い必須ルールと、この文書への参照。
- `PROJECT.md`: PJ目的、作業入口、正本関係、恒久的な構造、採用済み重要判断。タスク、履歴、参照元ログは置かない。
- `docs/README.md`: docs 入口。
- `docs/guide/docs-management-rules.md`: PJ docs update policy の正本。
- `docs/guide/docs-management-matrix-result-diagram.md`: 文書関係と更新漏れ防止の仕組み図。
- `docs/imp/user-tasks.md`, `docs/imp/user-judge.md`, `docs/imp/imp-tasks.md`, `docs/imp/imp-comp.md`: 進行管理の最小セット。
- `.agents/README.md`: `.agents/` 配下へ docs 更新判断表を重複コピーしないための案内。
- `G:\knowledge-vault\knowledge-vault-write-policy.md`: 横断ナレッジ更新判断の中央正本。PJへコピーせず参照する。

`.agents/` 配下の skills や commands を引き継ぐ場合でも、docs 更新ルールの正本はこの文書に置く。
agent / skill 側へ同じ判断表をコピーせず、必要な場合はこの文書を参照させる。
