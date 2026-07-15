# Linux Listening Lounge 配信手順

作成日: 2026-07-12

## 目的

Windows上で検証済みのHub本流 `Listening Lounge` と、Hubのサイドメニューに合わせたVikunja frontend forkを、既存Linuxサーバーへ反映する。Vikunjaの永続データは既存volumeを使い、stable版へ戻せるようにcustom imageを別tagで保持する。

この手順は、ソースbundleを `/tmp` に転送した後、Linux側のSSHセッションで実行する。Codex環境からはサーバーのSSH鍵認証が通らないため、転送・再構築を自動実行できない場合の正本手順でもある。

## 次回からの統一起動構成

次回のLinux配置では、HubとVikunjaを別Composeで起動せず、`infra/deploy/`を唯一の起動入口にする。

```text
<deploy-root>/
├── apps/web/                         # Hub source
├── build/vikunja-listening-lounge/   # fork source（なければbundleから起動scriptが展開）
└── infra/deploy/
    ├── compose.yaml                  # Hub + Listening Lounge Vikunja
    ├── .env                          # LAN IPと非secretのパスのみ
    └── start-pj-general.sh           # 一式起動
```

`infra/deploy/.env.example`を`.env`へコピーし、パスと`SERVER_LAN_IP`だけを設定する。token・password・secretは既存の`HUB_ENV_FILE` / `VIKUNJA_ENV_FILE`を参照し、`.env`へ書かない。

```bash
cd <deploy-root>/infra/deploy
cp .env.example .env
./start-pj-general.sh --dry-run
./start-pj-general.sh
```

この起動scriptはListening Lounge custom imageを既定とし、imageが無ければ`/tmp/vikunja-listening-lounge-working-tree.tgz`からfork sourceを展開してbuildする。volume削除、再インポート、secret表示は行わない。

旧来のHub/Vikunjaが別Composeで同名コンテナとして稼働中の場合、通常実行は安全のため停止する。その場合は、先に削除対象が**コンテナだけ**であることをdry-runで確認し、明示指定で統一起動構成へ引き継ぐ。

```bash
./start-pj-general.sh --start --adopt-existing --dry-run
./start-pj-general.sh --start --adopt-existing
```

`--adopt-existing` は旧`pj-general` / `vikunja`コンテナを`docker rm -f`で置き換えるだけである。named volume、bind mount上のDB/files、イメージ、データ再インポートには触れない。統一起動後の通常再実行では不要である。

Vikunja forkのソースを更新した回だけは、source bundleを`build/vikunja-listening-lounge/`へ展開後、次の一発でcustom imageを再buildしてHub / Vikunjaを起動する。

```bash
./start-pj-general.sh --start --rebuild-vikunja
```

`--rebuild-vikunja`はimageだけを再buildする。volume、DB、files、再インポートには触れない。

Linux側の`start-pj-general.sh`がこのオプションを知らない場合は、fork bundleより先にリポジトリの現行scriptを置き換える。これは起動手順だけの更新であり、DB / files / volume / env内容には触れない。

```powershell
scp G:\devwork\pj-general\infra\deploy\start-pj-general.sh unibell4@192.168.0.200:~/pj-general-deploy/infra/deploy/
```

```bash
cd ~/pj-general-deploy/infra/deploy
chmod +x start-pj-general.sh
grep -q -- '--rebuild-vikunja' start-pj-general.sh
```

`grep`が成功してからbundle展開と`--rebuild-vikunja`を実行する。`unknown argument: --rebuild-vikunja`はscriptが旧版であることを示すため、そのまま再試行しない。

統一Composeは、既存のVikunja環境でCORSが有効でも起動できるよう、非secretの`VIKUNJA_SERVICE_PUBLICURL`を`http://${SERVER_LAN_IP}:3456/`として明示する。secret envファイルの内容は表示・複製しない。

## Codexから接続する場合

秘密鍵をチャットやリポジトリへ貼らない。Codex側で作った一時鍵の公開鍵だけを、既存のLinux SSHセッションから `unibell4` の `authorized_keys` へ追加する。

```bash
umask 077
mkdir -p ~/.ssh
printf '%s\n' '<Codexが提示したssh-ed25519公開鍵1行>' >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Codexが非対話でDockerを操作するには、`sudo`のパスワード入力を使わずに済むよう、次のどちらかを選ぶ。

- 推奨: `sudo usermod -aG docker unibell4` を実行し、SSHを切断して再接続する。dockerグループはroot相当の権限を持つため、対象ユーザーを限定する。
- 代替: Docker操作だけを許可するsudoers drop-inを管理者が別途設計する。`NOPASSWD: ALL` は設定しない。

鍵登録と再接続後、Codex側で `ssh -i <一時秘密鍵> -o IdentitiesOnly=yes unibell4@192.168.0.200` を使って接続確認する。一時秘密鍵は配信完了後に削除する。

## 転送するbundle

リポジトリの次の2ファイルをサーバーへ転送する。

| bundle | 内容 | SHA-256 |
|---|---|---|
| `tmp/pj-general-web-working-tree.tgz` | Hub `apps/web` の現行Listening Lounge（Thread Line Hub薄橙識別・U02/U03操作ID照合と画面上のHTTP証跡を含む。テストとSQLiteを含めない） | `84A85F4398856176441C8490E5A73104844353C8A0BB7E17883A071626B286C8` |
| `tmp/vikunja-listening-lounge-working-tree.tgz` | Vikunja frontend forkの現行working tree（Thread Line Tasks薄青識別・Inboxアイコン・RV01〜RV04・Kanban guideのviewKind抑止・Tasks本文アクセントの青/淡青統一・Hubと同じタイトル面の塗り領域・プロジェクト／ラベル／チームの`マスタ管理`統合を含む。build生成物を含めない） | `D166BBCBCC56414D00E4278C4710B91FC750054902CEAF9DA090D82DCF39B85D` |
| `tmp/pj-general-p1-sync-working-tree.tgz` | P1 worker / reconcile / backup / restore / PoC / systemd / Vikunja切替スクリプト | `6A73873F8D6119F61AC170B0BB3AF5BDAC13B7BD9C5F7BBB8F1B39B880659CD5` |

Windows PowerShellの例:

```powershell
scp G:\devwork\pj-general\tmp\pj-general-web-working-tree.tgz unibell4@192.168.0.200:/tmp/
scp G:\devwork\pj-general\tmp\vikunja-listening-lounge-working-tree.tgz unibell4@192.168.0.200:/tmp/
scp G:\devwork\pj-general\tmp\pj-general-p1-sync-working-tree.tgz unibell4@192.168.0.200:/tmp/
```

Linux側で転送後にhashを確認する。

```bash
sha256sum /tmp/pj-general-web-working-tree.tgz /tmp/vikunja-listening-lounge-working-tree.tgz
```

## P0フロントの一行再配信（現行手順）

### パスワードなしの前提準備

通常の再配信は、SSH公開鍵と`unibell4`のdockerグループ権限だけで行う。`~/pj-general-deploy`は`unibell4`が所有し、再配信helperと`start-pj-general.sh`は`sudo`を使わない。`docker`グループはroot相当であるため、追加するのはこの専用ユーザーだけとし、`NOPASSWD: ALL`は設定しない。

Windowsでは専用鍵を作り、公開鍵だけをLinuxの`~/.ssh/authorized_keys`へ追加する。秘密鍵はWindows側から持ち出さず、リポジトリにも置かない。

```powershell
ssh-keygen -t ed25519 -a 100 -f "$env:USERPROFILE\.ssh\codex_pjserver_ed25519" -C "codex-pjserver"
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add "$env:USERPROFILE\.ssh\codex_pjserver_ed25519"
```

Linuxの既存SSH接続内で、表示した公開鍵の1行だけを登録する。

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
printf '%s\n' '<Windowsで表示した公開鍵1行>' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

鍵のpassphraseは`ssh-add`時にWindowsログインごとに一度だけ入力する。再配信scriptは`BatchMode=yes`で実行するため、鍵またはagent登録がない場合にパスワード入力へフォールバックしない。

P0フロントのHub / Tasks sourceを更新する場合、CodexがWindowsから次の一行を直接実行する。ユーザーはPowerShellやSSHを開かない。前提準備後は`BatchMode=yes`で実行し、対話パスワード入力を求めない。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File G:\devwork\pj-general\infra\deploy\redeploy-p0-frontend.ps1
```

- script自身が実行直前にローカルの現行 `apps/web` と `tmp/vikunja-listening-lounge` からsource-only bundleを再作成し、そのbundleのSHA-256を表示してLinux側でも照合する。古い `tmp/*.tgz` を再利用しないため、資材更新のたびにユーザーがbundleを作り直す必要はない。文書へhashを手入力しない。
- 既定鍵は、すでにLinuxへ公開鍵登録済みの`%USERPROFILE%\.ssh\codex_pjserver_ed25519`であり、`-IdentityFile`で明示変更できる。秘密鍵は表示・転送・Git保存しない。
- Hub / Tasks sourceと`start-pj-general.sh`だけを転送・展開し、`--rebuild-vikunja`で一式を再buildする。
- DB、files、volumeを削除せず、再インポート、env内容表示、secret保存も行わない。
- `/api/bootstrap`と`/api/v1/info`がともに200でない場合、成功扱いにせず停止する。
- 事前確認だけなら末尾に`-DryRun`を付ける。

### Codexへ委任する範囲

- Codexは、対象sourceのテスト成功と差分確認後に、`-DryRun`、通常再配信、両API 200とSQLite integrity・件数の読取り確認まで直接実行してよい。
- この委任は`redeploy-p0-frontend.ps1`が保証するsource-only、hash照合、sudo不要、DB/files/volume非削除、再インポートなしの経路に限定する。
- sudo、docker groupや`authorized_keys`の変更、secret/env設定、実データ取込、GO、rollbackでデータへ触れる操作は含めない。必要になった時点でユーザーへ戻す。
- デプロイのためだけにユーザーへPowerShell一行の実行を依頼しない。鍵がagentへ未登録、鍵ファイルがない、BatchModeで接続できない場合は、Codexが原因を切り分けて必要な最小ユーザー操作だけを依頼する。

## Hubの再ビルドと切替

既存DBを消さず、`apps/web` のソースだけを更新する。サーバー上のCompose定義が `infra/vikunja/pj-general.compose.example.yaml` 相当であることを確認してから実行する。

```bash
sudo mkdir -p /srv/pj-general
sudo tar -xzf /tmp/pj-general-web-working-tree.tgz -C /srv/pj-general
cd /srv/pj-general/stack
sudo docker compose build pj-general
sudo docker compose up -d --force-recreate --no-deps pj-general
```

反映確認:

```bash
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
curl -fsS http://192.168.0.200:4173/api/health
curl -fsS http://192.168.0.200:4173/ | grep -E 'Listening Lounge|chat-model-meta' >/dev/null
```

`/api/health` がない場合は、旧イメージが起動しているか、Composeが別のサービス定義を参照している。`sudo docker inspect pj-general --format '{{.Config.Image}}'` と `sudo docker compose config` で確認する。

## Hub / Vikunja recovery helper

`infra/vikunja/recover-pj-general.sh` は、HubコンテナのDocker Compose labelから実際のCompose定義を自動特定する復旧補助である。`/srv/pj-general/stack`のような別Composeを誤って操作しないため、復旧前に必ず`--status`または`--dry-run`を実行する。

Windowsから転送する場合:

```powershell
scp G:\devwork\pj-general\infra\vikunja\recover-pj-general.sh unibell4@192.168.0.200:/tmp/
```

Linuxの対話SSH端末で配置して実行する。

```bash
sudo install -m 0750 /tmp/recover-pj-general.sh /home/unibell4/pj-general-deploy/infra/vikunja/recover-pj-general.sh
cd /home/unibell4/pj-general-deploy/infra/vikunja

./recover-pj-general.sh --status
./recover-pj-general.sh --redeploy-hub --dry-run
./recover-pj-general.sh --redeploy-hub
./recover-pj-general.sh --restart-all
```

- `--redeploy-hub` は`/tmp/pj-general-web-working-tree.tgz`を、検出したdeploy rootへ展開してHubだけをrebuild・recreateする。
- `--restart-all` はHubを再作成し、Vikunjaは既定で`rohto4/vikunja:2.3.0-pj-general-listening-lounge`を再作成する。別imageにする場合だけ`--vikunja-image IMAGE`を指定する。image buildはしない。
- volume削除、Compose project全体の停止、データ再インポート、env内容の表示は行わない。

## P1定期sync workerの登録

Slack / Misskey workerのsource-only実装とfake回帰は完了しているが、この通常配信手順ではworkerを登録・有効化しない。workerはHubと同じSQLiteを使うため、実運用はユーザーがrepo外の最小権限envを設定し、手動dry-run 1回と明示`--commit` 1回を承認した後に分離して行う。`sync.env.example`は値を入れずに参照する雛形であり、secretをGit・ログ・チャットへ出さない。

timer有効化は、source別runとpending候補の品質を`/api/observability`で受入した後だけにする。具体的な契約と登録順は`docs/arch/linux-periodic-intake-architecture.md`と`docs/ops/p0-operations-runbook-2026-07.md`を正本とする。

Hub復旧後のVikunja状態再照合は、同じbundleのreconcile timerで15分ごとに実行できる。

```bash
sudo install -m 0644 /srv/pj-general/infra/systemd/pj-general-reconcile.service /etc/systemd/system/pj-general-reconcile.service
sudo install -m 0644 /srv/pj-general/infra/systemd/pj-general-reconcile.timer /etc/systemd/system/pj-general-reconcile.timer
sudo install -m 0600 /srv/pj-general/infra/systemd/reconcile.env.example /etc/pj-general/reconcile.env
sudo systemctl daemon-reload
sudo systemctl enable --now pj-general-reconcile.timer
sudo systemctl start pj-general-reconcile.service
sudo journalctl -u pj-general-reconcile.service -n 100 --no-pager
```

## DB / files backupの登録

同じworker bundleに、Hub SQLite、Vikunja SQLite、files、secret設定を世代単位で退避するbackup timerも含まれる。外部媒体へ複製する場合だけ、`/etc/pj-general/backup.env` の `MIRROR_ROOT` にマウント済みパスを設定する。

```bash
sudo install -m 0644 /srv/pj-general/infra/systemd/pj-general-backup.service /etc/systemd/system/pj-general-backup.service
sudo install -m 0644 /srv/pj-general/infra/systemd/pj-general-backup.timer /etc/systemd/system/pj-general-backup.timer
sudo install -m 0600 /srv/pj-general/infra/systemd/backup.env.example /etc/pj-general/backup.env
sudo systemctl daemon-reload
sudo systemctl enable --now pj-general-backup.timer
sudo systemctl start pj-general-backup.service
sudo journalctl -u pj-general-backup.service -n 100 --no-pager
```

世代保持は `KEEP_GENERATIONS=7` が既定で、生成世代に `manifest.sha256` を作る。初回実行後はbackup世代とrestore-testの件数を確認してから常用する。

## P1 dry-run PoC

実運用データを変更せず、類似候補と部分自動確定条件だけを確認できる。

```bash
python3 /srv/pj-general/workers/poc/dry_run.py --db /home/unibell4/.local/share/pj-general/p0.sqlite --mode similarity
python3 /srv/pj-general/workers/poc/dry_run.py --db /home/unibell4/.local/share/pj-general/p0.sqlite --mode partial-auto-confirm
```

どちらも`dryRun=true`を返し、candidateやdecisionを更新しない。自動GOへ接続してはいけない。

## Vikunja frontend forkのビルドと切替

先にデータ領域をbackupし、custom imageをstable版と別tagで作る。DB schemaを変更するアップグレードは同時に行わない。

```bash
sudo mkdir -p /srv/pj-general/build/vikunja-listening-lounge
sudo tar -xzf /tmp/vikunja-listening-lounge-working-tree.tgz -C /srv/pj-general/build/vikunja-listening-lounge
cd /srv/pj-general/build/vikunja-listening-lounge
sudo VIKUNJA_SOURCE_DIR=/srv/pj-general/build/vikunja-listening-lounge /srv/pj-general/infra/vikunja/build-listening-lounge.sh
```

Composeでimageを一時指定して切り替える。

```bash
cd /srv/pj-general/stack
sudo /srv/pj-general/infra/vikunja/switch-image.sh rohto4/vikunja:2.3.0-pj-general-listening-lounge
```

確認:

```bash
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
curl -fsS http://192.168.0.200:3456/api/v1/info
```

ブラウザではログイン、Home、Dashboard、Inbox List、Table、Kanban、Gantt、Task detail、`マスタ管理`を確認する。サイドバーは`Thread Line Tasks`のタイトル面、Hubと同じ208px幅、書体、罫線、Tasks青の選択線、hover時5px横移動で表示されることを確認する。`マスタ管理`ではプロジェクト・ラベル・チームを同一画面で確認し、追加導線がそれぞれ動くことを確認する。

## 旧版へのrollback

データvolumeを削除せず、参照imageだけをstableに戻す。

```bash
cd /srv/pj-general/stack
sudo /srv/pj-general/infra/vikunja/switch-image.sh vikunja/vikunja:2.3.0
```

Hubだけを戻す必要がある場合は、直前の `pj-general/web:p0` imageを確認してから、ソースbundleを戻し、同じ `build` / `up` を実行する。

## upstream追随と再配信

Vikunjaのunstable APIへ追随せず、stable `v2.3.0`のfrontend差分だけを更新する。更新は作業branchで行い、custom imageを置き換える前に差分・unit test・production build・bundle hashを保存する。

```bash
cd /srv/pj-general/build/vikunja-listening-lounge
sudo git remote -v
sudo git fetch upstream --tags
sudo git log --oneline --decorate -5
sudo git diff --stat vikunja/v2.3.0...325bc5475
sudo git range-diff vikunja/v2.3.0...325bc5475 vikunja/v2.3.0...HEAD
sudo git rebase vikunja/v2.3.0
sudo pnpm --dir frontend test:unit -- --run --exclude 'tests/e2e/**'
sudo pnpm --dir frontend lint:styles
sudo pnpm --dir frontend build
sudo VIKUNJA_SOURCE_DIR=/srv/pj-general/build/vikunja-listening-lounge /srv/pj-general/infra/vikunja/build-listening-lounge.sh
sudo sha256sum /tmp/vikunja-listening-lounge-working-tree.tgz
```

`range-diff`でdashboard / guide / theme以外の意図しない差分が出た場合は配信を止める。custom imageを起動した後は、login、Dashboard、Inbox、List、Table、Kanban、Gantt、Task detailを確認し、問題があれば`switch-image.sh vikunja/vikunja:2.3.0`でstableへ戻す。rollback後もDB / files volumeを削除せず、件数・execution link・外部task IDを比較する。

## 既知の制約

- `docker` は一般ユーザーでは `/var/run/docker.sock` 権限不足になるため、現在のサーバーでは `sudo docker` を使う。
- コンテナのportは `192.168.0.200` にbindされているため、サーバー上の疎通確認は `127.0.0.1` ではなく `192.168.0.200` を使う。
- 旧Hubは `/api/health` が404で、HTMLにもListening Lounge / AI相談の現行マーカーがない。再起動だけでは更新されないため、Hubは必ず再buildする。
