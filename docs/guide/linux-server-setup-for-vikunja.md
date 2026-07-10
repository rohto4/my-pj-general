# Vikunja / pj-general向け Linuxサーバー構築手順

作成日: 2026-07-11

## 目的

Windows 11のミニPCを、Vikunjaとpj-generalを同一ホスト上で動かすLinuxサーバーへ移行する。

このガイドの完了時点では、次の実装を開始できる状態にする。

- Ubuntu Serverの導入
- SSHによるリモート管理
- 固定的に参照できるLAN内IP
- Docker EngineとDocker Compose
- Vikunja用の永続データ領域
- pj-generalとVikunjaを接続するDocker内部ネットワーク
- API token、Webhook secretを保管できる権限分離されたディレクトリ
- ルーター外部公開なしの安全な初期検証環境

Vikunjaの実起動、プロジェクト作成、API token発行、Webhook作成、pj-generalとの実データ結合は、このサーバー準備後に実施する。

## 推奨構成

今回の実機構築では、計画どおりUbuntu Server 24.04.4 LTSを採用する。Docker公式のサポート対象でもあり、今回のVikunja / pj-general実データ結合用の固定した初期環境として扱う。

- OS: Ubuntu Server 24.04.4 LTS amd64
- CPU: IntelまたはAMDの64bit CPU
- RAM: 8GB以上を推奨
- ストレージ: SSD 64GB以上を推奨
- ネットワーク: 有線LAN
- 実行方式: Docker Engine + Docker Compose
- 初期DB: SQLiteの永続マウント
- 将来の常設運用: PostgreSQLへ移行

Ubuntu 26.04のISOを一度マウントしていても問題ない。今回はUbuntu Server 24.04.4 LTSのISOを別途ダウンロードし、RufusでUSBへ書き込む。

## 重要な注意

以下の手順は、Windows 11を消去してミニPCをLinux専用サーバーにする前提である。

「ディスク全体を使用」を選ぶと、Windows、アプリ、ユーザーデータが削除される。

実行前に、次を別のストレージへバックアップする。

- Windows上の個人ファイル
- SSH鍵
- ブラウザの必要なデータ
- GitHubなどの認証情報
- 後で再取得できない設定ファイル

Windowsを残す場合は、この手順のストレージ設定を使わず、デュアルブート構成を別途設計する。

## 全体構成

初期検証では、Vikunjaのポートをインターネットへ公開しない。

~~~text
[Windowsのブラウザ]
        |
        | SSHトンネル
        v
[Ubuntu Server: pj-server]
        |
        +-- Docker network: pj-general-net
             |
             +-- vikunja:3456
             |
             +-- pj-general:<内部ポート>
                         ^
                         |
                  Webhook受信
~~~

コンテナ間通信では、localhostではなくサービス名を使う。

- pj-generalからVikunja: http://vikunja:3456
- Vikunjaからpj-general: http://pj-general:<内部ポート>/api/integrations/vikunja/webhook

実際のAPI resource pathとpj-generalの内部ポートは、デプロイするVikunja releaseと実装結果に合わせて確定する。

## 1. Ubuntu ServerのISOを用意する

Windows上でUbuntu Serverのamd64版ISOをダウンロードする。

通常のファイル名は次の形式になる。

~~~text
ubuntu-24.04.4-live-server-amd64.iso
~~~

ISOはUSBメモリへ直接コピーせず、Rufusなどのイメージライターで書き込む。

ISOのSHA256を確認する。

~~~powershell
Get-FileHash "$HOME\Downloads\ubuntu-24.04.4-live-server-amd64.iso" -Algorithm SHA256
~~~

表示された値をUbuntu公式配布ページのSHA256SUMSと照合する。

## 2. 起動用USBを作成する

Rufusを使う場合の設定は次のとおり。

1. USBメモリをWindows PCへ接続する。
2. Rufusを起動する。
3. 正しいUSBデバイスを選択する。
4. Boot selectionでUbuntu ISOを選択する。
5. Partitioning schemeをGPTにする。
6. Target systemをUEFIにする。
7. Startを押す。
8. 書き込み方式を聞かれたらISO Image modeを選択する。
9. 完了するまで待つ。

USBの内容は全消去される。USB内に必要なファイルが残っていないことを確認してから実行する。

## 3. ミニPCへUbuntu Serverをインストールする

1. ミニPCへ有線LANを接続する。
2. 作成したUSBを挿入する。
3. 電源を入れ、F12、F2、Escなどでブートメニューを開く。
4. UEFI: USBの項目を選択する。
5. Ubuntu Serverのインストーラーを起動する。

インストーラーでは次のように設定する。

| 項目 | 設定 |
|---|---|
| Language | 任意 |
| Keyboard | 実際のキーボードに合わせる |
| Network | 有線LANのDHCP |
| Proxy | 通常は空欄 |
| Storage | Use an entire disk |
| Hostname | pj-server |
| User | 例: ops |
| SSH Server | 有効 |
| 追加Snap | なし |

Storageで対象ディスクを必ず確認する。Windowsを消去して専用サーバーにする場合だけ、Use an entire diskを選択する。

インストールが完了したら再起動し、USBメモリを抜く。

## 4. 初回ログインと基本設定

ミニPC本体で作成したユーザーとしてログインする。

~~~bash
sudo apt update
sudo apt full-upgrade -y

sudo apt install -y ca-certificates curl git jq htop ncdu openssl ufw unattended-upgrades

sudo timedatectl set-timezone Asia/Tokyo

hostnamectl
timedatectl
~~~

サーバー名が正しくない場合は、次で設定する。

~~~bash
sudo hostnamectl set-hostname pj-server
~~~

## 5. ルーターでIPアドレスを固定する

まず、IPアドレスとMACアドレスを確認する。

~~~bash
ip -br addr
ip -br link
~~~

ルーターのDHCP設定で、このミニPCのMACアドレスに固定IPを割り当てる。

例:

~~~text
Hostname: pj-server
固定割当IP: 192.168.1.50
~~~

初期段階では、Ubuntu側で手動の静的IP設定をするより、ルーター側のDHCP予約を推奨する。

## 6. SSH鍵で接続する

### Windows側で鍵を作る

PowerShellで実行する。

~~~powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\pj-server_ed25519" -C "pj-server"
Get-Content "$env:USERPROFILE\.ssh\pj-server_ed25519.pub"
~~~

表示された公開鍵1行をコピーする。

### Ubuntu側へ公開鍵を登録する

Ubuntu側で実行する。

~~~bash
install -d -m 700 ~/.ssh
nano ~/.ssh/authorized_keys
~~~

コピーした公開鍵を貼り付けて保存する。

~~~bash
chmod 600 ~/.ssh/authorized_keys
~~~

Windows側から鍵接続を確認する。

~~~powershell
ssh -i "$env:USERPROFILE\.ssh\pj-server_ed25519" ops@192.168.1.50
~~~

ユーザー名とIPアドレスは実際の値に置き換える。

### SSHのパスワードログインを停止する

鍵接続を確認できた後に実行する。

~~~bash
sudo nano /etc/ssh/sshd_config.d/60-hardening.conf
~~~

次の内容を保存する。

~~~text
PubkeyAuthentication yes
PasswordAuthentication no
PermitRootLogin no
~~~

設定を検査して反映する。

~~~bash
sudo sshd -t
sudo systemctl reload ssh
~~~

既存のSSH接続を閉じる前に、新しいPowerShellから鍵接続できることを再確認する。

## 7. Firewallを設定する

以下の例ではLANを192.168.1.0/24としている。実際のLAN CIDRに置き換える。

~~~bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp
sudo ufw --force enable
sudo ufw status verbose
~~~

初期検証では、Vikunjaの3456番ポートを外部公開しない。

Dockerで公開したポートはUFWを迂回する場合があるため、DockerコンテナのポートをUFWだけで保護できるとは考えない。ルーター側のポート転送も設定しない。

## 8. SSHトンネルでVikunjaを確認する

Vikunjaを3456番ポートで起動した後、Windows側で次を実行する。

~~~powershell
ssh -N -L 3456:127.0.0.1:3456 -i "$env:USERPROFILE\.ssh\pj-server_ed25519" ops@192.168.1.50
~~~

このPowerShellを開いたまま、ブラウザで次を開く。

~~~text
http://127.0.0.1:3456
~~~

## 9. Docker EngineとDocker Composeをインストールする

Docker公式APTリポジトリを登録する。

~~~bash
sudo apt update
sudo apt install -y ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "$UBUNTU_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
~~~

Dockerを起動時に自動起動する。

~~~bash
sudo systemctl enable --now docker
sudo systemctl is-active docker
~~~

管理ユーザーからsudoなしでDockerを使う場合は、次を実行する。

~~~bash
sudo usermod -aG docker "$USER"
newgrp docker
~~~

Dockerグループは実質的にroot相当の権限を持つ。専用の管理ユーザーだけを追加する。

動作確認する。

~~~bash
docker run --rm hello-world
docker --version
docker compose version
~~~

## 10. 永続データ領域を作る

VikunjaのDBや添付ファイルをコンテナ内部だけに保存しない。

~~~bash
sudo mkdir -p /srv/pj-general/stack /srv/pj-general/data/vikunja/files /srv/pj-general/data/vikunja/db /srv/pj-general/backups /srv/pj-general/secrets
sudo chown -R "$USER":"$USER" /srv/pj-general
sudo chmod 700 /srv/pj-general/secrets
sudo chown -R 1000:1000 /srv/pj-general/data/vikunja/files /srv/pj-general/data/vikunja/db
~~~

構成は次のとおり。

| パス | 用途 |
|---|---|
| /srv/pj-general/stack | Compose定義 |
| /srv/pj-general/data/vikunja/files | Vikunja添付ファイル |
| /srv/pj-general/data/vikunja/db | 初期検証用SQLite |
| /srv/pj-general/backups | バックアップ一時領域 |
| /srv/pj-general/secrets | Secretファイル |

同一ディスク上のbackupsは本当のバックアップではない。常設運用へ移行する前に、別PC、NAS、外付けディスクなどへ複製する。

## 11. Docker内部ネットワークを作る

~~~bash
docker network create pj-general-net
docker network inspect pj-general-net
~~~

後でVikunjaとpj-generalを、この同じネットワークへ接続する。

コンテナ間の接続先は次のようにする。

~~~text
pj-general -> http://vikunja:3456
vikunja -> http://pj-general:<内部ポート>/api/integrations/vikunja/webhook
~~~

コンテナ間通信でlocalhostを使うと、自分自身のコンテナへ接続してしまう。

## 12. Secret保管場所を準備する

リポジトリ内、SQLite、ログ、画面表示にはSecretを書かない。

Vikunja本体用のSecretを生成する。

~~~bash
sudo sh -c 'umask 077; printf "VIKUNJA_SERVICE_SECRET=%s\n" "$(openssl rand -hex 32)" > /srv/pj-general/secrets/vikunja.env'
sudo chmod 600 /srv/pj-general/secrets/vikunja.env
~~~

Vikunja本体の設定と、pj-generalが使うAPI token / Webhook secretは分離する。

| 実ファイル | 雛形 | 所有する値 |
| --- | --- | --- |
| `/srv/pj-general/secrets/vikunja.env` | `infra/vikunja/vikunja.env.example` | Vikunja server設定と`VIKUNJA_SERVICE_SECRET` |
| `/srv/pj-general/secrets/pj-general.env` | `infra/vikunja/pj-general.env.example` | API token、project ID、Webhook secret |

初回起動は`VIKUNJA_SERVICE_ENABLEREGISTRATION=true`で管理ユーザーを作成し、その後`false`へ変更して再起動する。内部Docker network上のWebhook送信には`VIKUNJA_OUTGOINGREQUESTS_ALLOWNONROUTABLEIPS=true`が必要になる。

後で次の値を`pj-general.env`へ追加する。

| Secret | 作成時期 | 用途 |
|---|---|---|
| VIKUNJA_SERVICE_SECRET | サーバー準備時 | Vikunja内部Secret |
| VIKUNJA_API_TOKEN | Vikunja初回設定後 | pj-generalからVikunja APIを呼ぶ |
| VIKUNJA_WEBHOOK_SECRET | Webhook作成時 | WebhookのHMAC署名検証 |

API tokenはVikunjaのユーザーとプロジェクトを作成した後、画面から発行する。

Webhook secretはVikunja側のWebhook作成時に設定し、pj-general側でも同じSecretを読み込む。

## 12.1 Vikunjaを固定バージョンで起動する

初回実機検証では`infra/vikunja/compose.example.yaml`をサーバーへ配置し、Vikunja `2.3.0`を固定して使う。`latest`は使わない。

~~~bash
cd /srv/pj-general
cp <repository>/infra/vikunja/compose.example.yaml compose.yaml
docker compose config
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=100 vikunja
~~~

APIの初回契約は`/api/v1`であり、task作成は`PUT /api/v1/projects/{project}/tasks`を使う。mainのAPI v2へ追随する場合は、先にadapter契約と受入試験を更新する。

## 13. サーバー準備の完了確認

Ubuntu上で次を実行する。

~~~bash
uname -m
. /etc/os-release && echo "$PRETTY_NAME"

systemctl is-active ssh
systemctl is-active docker

docker --version
docker compose version

ip -br addr
df -h /srv

sudo ufw status verbose
docker network inspect pj-general-net > /dev/null
~~~

次の状態なら、Vikunja実データ結合の開始ゲートを満たしている。

- uname -mがx86_64
- Ubuntu Server 24.04.4 LTS
- WindowsからSSH鍵で接続できる
- sshとdockerがactive
- Docker Composeが実行できる
- /srv/pj-generalに永続領域がある
- pj-general-netが存在する
- Secretファイルが600である
- ルーターのポート転送を設定していない

## 14. サーバー準備後に実施する作業

サーバー準備後は、次の順番で実データ結合へ進む。

1. Vikunjaを公式Dockerイメージで起動する。
2. Vikunjaの画面へログインする。
3. 実在するプロジェクトを作成する。
4. API tokenを作成する。
5. pj-generalから実際の候補を1件GOする。
6. Vikunjaにtaskが1件だけ作成されることを確認する。
7. Vikunja側でtaskを完了・期限変更する。
8. pj-generalのWebhook受信処理で状態が反映されることを確認する。
9. 署名不正、二重イベント、API失敗、再試行を検証する。
10. 実データ結合後にPostgreSQL、HTTPS、バックアップを追加する。

VikunjaのWebhookは、設定したSecretを使ってX-Vikunja-SignatureにHMAC-SHA256署名を付ける。pj-general側はraw bodyで署名を検証し、イベントを冪等に保存する。

## 公式参照

- [Ubuntu Serverのダウンロード](https://ubuntu.com/download/server)
- [Ubuntu公式USB作成手順](https://ubuntu.com/desktop/docs/en/latest/how-to/create-a-bootable-usb-stick/)
- [Ubuntu Server基本インストール](https://ubuntu.com/server/docs/tutorial/basic-installation/)
- [Ubuntu OpenSSH公式手順](https://ubuntu.com/server/docs/openssh-server/)
- [Ubuntu Firewall公式手順](https://documentation.ubuntu.com/server/how-to/security/firewalls/)
- [Docker EngineをUbuntuへインストール](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose Plugin](https://docs.docker.com/compose/install/linux/)
- [Docker Linux後処理](https://docs.docker.com/engine/install/linux-postinstall/)
- [DockerとFirewallの注意点](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
- [Vikunjaインストール](https://vikunja.io/docs/installing/)
- [Vikunja公式Docker例](https://vikunja.io/docs/full-docker-example/)
- [Vikunja APIドキュメント](https://vikunja.io/docs/api-documentation/)
- [Vikunja Webhook API](https://vikunja.io/docs/webhooks/)

## PJ内の関連資料

- [Vikunja / pj-general Linux配置・運用設計](../arch/vikunja-linux-deployment-and-operations-2026-07.md)
- [Vikunja / pj-general結合アーキテクチャ](../arch/vikunja-pj-general-integration-architecture-2026-07.md)
- [Vikunja結合契約](../spec/vikunja-integration-contract-2026-07.md)
- [Vikunja結合タスク](../imp/vikunja-integration-tasks.md)
