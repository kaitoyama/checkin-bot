# Check-in Bot

Discord 上でイベント参加の受付を行う簡易ボットです。discord.py v2 の Component（ボタン）を使って参加フローを実装しています。

主要機能
- `/set` を実行したチャンネルに「イベントへの参加はこちらから!」というメッセージを投稿し、参加ボタンを表示します。
- 参加ボタンを押すと、押したユーザーにだけ見える（ephemeral）確認メッセージが表示され、再度確認ボタンで参加を確定できます。
- 参加確定時にタイムスタンプとユーザーID（およびサーバ/チャンネル情報）を記録します。


記録先
- Google Sheets（サービスアカウント）にのみ記録します。`SPREADSHEET_ID` とサービスアカウント資格情報（ファイル、JSON文字列、または項目ごとの環境変数のいずれか）を設定してください。

セットアップ

1. Python 3.8+ を用意します。
2. 仮想環境を作って依存をインストールします。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Discord アプリ（Bot）を作成し、Bot トークンを取得して環境変数 `DISCORD_TOKEN` に設定します。

4. Google Sheets を使用するためにサービスアカウントを作成し、`SPREADSHEET_ID` と資格情報を設定してください。サービスアカウントにスプレッドシートの編集権限を付与してください。


Google Sheets の資格情報の設定方法は3種類あります。

1. ファイルパスを渡す
	- `GOOGLE_SERVICE_ACCOUNT_FILE` にダウンロードした JSON キーファイルのパスを設定します。
2. JSON 文字列を直接渡す
	- `GOOGLE_SERVICE_ACCOUNT_JSON` に JSON キーの内容そのものを設定します。
3. 項目ごとに環境変数を渡す
	- 以下の環境変数を全てセットします。
	  - `GOOGLE_SERVICE_ACCOUNT_TYPE`
	  - `GOOGLE_SERVICE_ACCOUNT_PROJECT_ID`
	  - `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID`
	  - `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` （改行は `\n` として表現）
	  - `GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL`
	  - `GOOGLE_SERVICE_ACCOUNT_CLIENT_ID`
	  - `GOOGLE_SERVICE_ACCOUNT_AUTH_URI`
	  - `GOOGLE_SERVICE_ACCOUNT_TOKEN_URI`
	  - `GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL`
	  - `GOOGLE_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL`

環境変数例（`.env`）

```
DISCORD_TOKEN=your-discord-token
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
SPREADSHEET_ID=xxxxxxxxxxxxxxxxxxxx
```

JSON 文字列を使う場合

```
DISCORD_TOKEN=your-discord-token
SPREADSHEET_ID=xxxxxxxxxxxxxxxxxxxx
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...","client_email":"service-account@your-project.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project.iam.gserviceaccount.com"}
```

項目ごとの環境変数を使う場合

```
DISCORD_TOKEN=your-discord-token
GOOGLE_SERVICE_ACCOUNT_TYPE=service_account
GOOGLE_SERVICE_ACCOUNT_PROJECT_ID=your-project
GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID=...
GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...
GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL=service-account@your-project.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_CLIENT_ID=...
GOOGLE_SERVICE_ACCOUNT_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_SERVICE_ACCOUNT_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project.iam.gserviceaccount.com
SPREADSHEET_ID=xxxxxxxxxxxxxxxxxxxx
```

実行

```bash
export DISCORD_TOKEN=your-discord-token
export SPREADSHEET_ID=xxxxxxxxxxxxxxxxxxxx
# いずれか1つの方法で資格情報を渡す
export GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service_account.json
# export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
# export GOOGLE_SERVICE_ACCOUNT_TYPE=service_account
python bot.py
```

使い方
- サーバ上で `/set` を入力してコマンドを実行すると、そのチャンネルに参加メッセージが投稿されます。
- 参加ボタンを押すと、個別の確認ダイアログが表示され、参加確定を押すと記録されます。


注意点
- 参加ボタンは persistent view（永続化）で実装されているため、ボット再起動後も有効です。
- Google Sheets の設定が必須です。未設定の場合は起動時にエラーとなります。
