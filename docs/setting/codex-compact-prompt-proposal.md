# Codex compact 復帰設定

## 目的

コンテキスト自動圧縮後に、圧縮要約だけで作業を再開せず、最初の通常回答や作業継続より前に `AGENTS.md` から初期化ファイル群を再読み込みする動作を促す。

## 現状

- `C:\Users\unibe\.codex\config.toml` は存在する。
- `compact_prompt` は未設定。
- `experimental_compact_prompt_file` は未設定。
- `C:\Users\unibe\.codex` 直下に compact prompt 用ファイルは存在しない。
- `C:\Users\unibe\.codex\AGENTS.md` には圧縮時の初期化ファイル再読み込みルールがある。
- 公式 manual では `PreCompact` / `PostCompact` hook があり、matcher は `manual` / `auto` を取れる。
- 公式 manual では `SessionStart` hook の start source に `compact` がある。
- 2026-07-09 時点で `C:\Users\unibe\.codex\hooks.json`、`C:\Users\unibe\.codex\hooks\post_compact_reminder.ps1`、`C:\Users\unibe\.codex\hooks\session_start_compact_reminder.ps1` を作成済み。
- 2026-07-09 時点で `C:\Users\unibe\.codex\AGENTS.md` に compact 復帰の最優先ルールを追記済み。
- 2026-07-09 時点で `C:\Users\unibe\.codex\config.toml` に Memories を有効化する設定を追記済み。

## compact prompt override を使う場合のバックアップ方針

現時点では `experimental_compact_prompt_file` を使わないため、この節は未適用。

将来 compact prompt override を使う場合、`compact_prompt.md` は既存ファイルの上書きではなく新規作成するため、専用バックアップは不要とする。

`config.toml` へは `experimental_compact_prompt_file` の参照行だけを追加する。変更時はバックアップファイルを増やさず、追加行の近くに今回作成した旨のコメントを残す。

`auth.json`、sqlite、logs、session、history はバックアップ対象にしない。

## 推奨設定方針

第一候補は compact prompt override ではなく hook とする。

理由:

- `PreCompact` / `PostCompact` は compact の前後に走る補助処理として設計されている。
- matcher で `manual` / `auto` を指定でき、自動圧縮だけに寄せた制御も可能。
- `SessionStart` の `compact` は、圧縮後に新しい実行文脈が始まる場面を拾える可能性がある。
- `experimental_compact_prompt_file` は history compaction prompt のオーバーライドであり、デフォルト prompt の元文章が不明なまま使うと既定の圧縮品質を壊す可能性がある。

## 実装済み hook

`C:\Users\unibe\.codex\hooks.json` に次を反映済み。

`PostCompact` は compact 直後に reminder と log を作る。`SessionStart compact` は compact 後の実行文脈開始時に reminder と log を作る。

```json
{
  "hooks": {
    "PostCompact": [
      {
        "matcher": "auto|manual",
        "hooks": [
          {
            "type": "command",
            "commandWindows": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\unibe\\.codex\\hooks\\post_compact_reminder.ps1",
            "statusMessage": "Recording compact recovery reminder"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "commandWindows": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\unibe\\.codex\\hooks\\session_start_compact_reminder.ps1",
            "statusMessage": "Checking compact recovery bootstrap"
          }
        ]
      }
    ]
  }
}
```

hook script は、Codex の文脈を直接編集せず、ログと目に見える reminder を残す小さな処理にしている。

生成物:

- `C:\Users\unibe\.codex\compact-recovery-reminder.md` に「圧縮後は AGENTS.md / PROJECT.md を読み直す」と書く。
- `C:\Users\unibe\.codex\logs\compact-recovery.log` に compact 発生時刻と cwd を追記する。
- script 内で secret、session transcript、auth 情報を読まない。

単体確認:

- `post_compact_reminder.ps1` を手動実行し、reminder / log 生成を確認済み。
- `session_start_compact_reminder.ps1` を手動実行し、reminder / log 生成を確認済み。
- Codex の hook として実際に発火するには、必要に応じて `/hooks` で review / trust する。

## global AGENTS.md

`C:\Users\unibe\.codex\AGENTS.md` に、次の趣旨を追記済み。

- compact、セッション移動、handoff、要約コンテキストからの再開を検知したら、通常回答、作業継続、ファイル編集、外部書き込みより前に、workspace の `AGENTS.md` と `PROJECT.md` をファイル実体から読み直す。
- 圧縮後要約は復帰の補助情報であり、`AGENTS.md` / `PROJECT.md` の代替正本として扱わない。

## Memories

`C:\Users\unibe\.codex\config.toml` に次を追記済み。

```toml
[features]
# 2026-07-09: compact後の復帰補助として、安定した運用ルールや既知の落とし穴を思い出せるよう有効化。
memories = true

[memories]
# 2026-07-09: 必須ルールの正本ではなく、compact復帰時の補助記憶として使う。
generate_memories = true
use_memories = true
disable_on_external_context = false
```

Memories は必須ルールの正本ではなく、あくまで compact 復帰時に「思い出しやすくする」補助層として扱う。

## compact prompt override の扱い

`experimental_compact_prompt_file` は追記差分ではなく、history compaction prompt のオーバーライドとして扱う。

Codex のデフォルト compact prompt の元文章を確認できるまでは、実設定への反映は保留する。

元文章を確認できた場合のみ、次の方針で `config.toml` へファイル参照を追加する。

```toml
# 2026-07-09: compact後にPJ初期化ファイル群を再読み込みさせるため追加。
experimental_compact_prompt_file = "C:\\Users\\unibe\\.codex\\compact_prompt.md"
```

理由:

- `config.toml` を読みやすく保てる。
- prompt 本文を単独でバックアップ・差分確認できる。
- 今後の調整時に `config.toml` の他設定へ触れずに済む。

## `compact_prompt.md` 案

以下は、差し込みたい最小追記内容である。

実際に `C:\Users\unibe\.codex\compact_prompt.md` を作成する場合は、Codex のデフォルト compact prompt の元文章を保持したうえで、末尾または適切な制約節へこの内容だけを追加する。元文章が確認できない場合は、実ファイルを作成しない。

```md
# 2026-07-09 追記: 圧縮後のPJ初期化ファイル再読み込み

コンテキスト自動圧縮、セッション移動、handoff 受領、または要約コンテキストからの再開を検知できる状態では、圧縮後の要約だけで初期化完了とみなさない。

圧縮後の最初の通常回答、作業継続、ファイル編集、外部書き込みより前に、現在の workspace の `AGENTS.md` を読み直し、そこに記載された読み込み順に従って必要な初期化ファイル群を再読み込みする。

`AGENTS.md` と `PROJECT.md` は、圧縮された会話要約ではなく、workspace 上の外部正本として扱う。圧縮後要約に両ファイルの内容が含まれていても、圧縮後の復帰時にはファイル実体を読み直す。

`compact_prompt.md` 側で直接指定する最小ブートストラップは次だけにする。詳細な読み込み順は `AGENTS.md` を正本にする。

1. `AGENTS.md`
2. `PROJECT.md`

再読み込み後、`AGENTS.md` の読み込み順に従って、現在のタスク、判断待ち、完了済み作業、docs 更新ルール、knowledge-vault 更新ルールを確認してから作業に戻る。

圧縮後要約と再読み込みしたファイルの内容が矛盾する場合は、ファイル実体を優先する。ただし、ユーザーの最新メッセージがある場合は、その最新指示を最優先する。
```

## 反映手順

1. `PostCompact` / `SessionStart compact` を採用した。
2. `C:\Users\unibe\.codex\hooks\` と `C:\Users\unibe\.codex\hooks.json` へ反映した。
3. hook script を手動実行し、`compact-recovery-reminder.md` と `compact-recovery.log` の生成を確認した。
4. Codex の `/hooks` で hook を確認し、必要なら trust する。
5. PJ 側に、変更意図と実施日を `docs/imp/imp-comp.md` へ記録する。

compact prompt override を使う場合だけ、次を追加で行う。

1. Codex のデフォルト compact prompt の元文章を公式 manual、ローカル実体、または upstream source から確認する。
2. 元文章を確認できた場合だけ、元文章を保持した `C:\Users\unibe\.codex\compact_prompt.md` を作成し、上記の最小追記を加える。
3. `config.toml` に、今回作成した旨のコメントと `experimental_compact_prompt_file` を追記する。
4. `config.toml` に既存の `experimental_compact_prompt_file` がある場合は、上書きせず差分確認する。

## 注意

この設定は圧縮処理への強い誘導であり、`AGENTS.md` や `PROJECT.md` を技術的に圧縮対象外へ指定するものではない。正確には、圧縮後に両ファイルを外部正本として再読み込みすることを促す設定である。

`experimental_compact_prompt_file` はオーバーライドであり、デフォルト prompt への自動追記ではない前提で扱う。元文章を確認できない場合は、デフォルト挙動を壊す可能性があるため適用しない。

より機械的に保証したい場合は、将来的に hook や Codex 側の正式な復帰イベントが使えるかを再確認する。
