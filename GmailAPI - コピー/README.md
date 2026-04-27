# Gmail API メール送信サンプル（Python）

このサンプルは、Python から Gmail API を使って特定の宛先にメールを送信します。

## 1. 事前準備（Google Cloud）

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. `Gmail API` を有効化
3. `OAuth 同意画面` を設定
4. `認証情報` で `OAuth クライアント ID` を作成（アプリの種類: デスクトップ）
5. ダウンロードした JSON を `credentials.json` という名前で、このフォルダに保存

## 2. インストール

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. 宛先設定

`send_gmail.py` の `DEFAULT_TO_EMAIL` を送信したい宛先に変更してください。

または、実行時に引数で指定できます。

## 4. 実行

初回実行時はブラウザが開き、Googleアカウント認証を行います。認証後 `token.json` が作成されます。

```bash
python send_gmail.py
```

送信先・件名・本文を指定する例:

```bash
python send_gmail.py --to your-target@example.com --subject "テスト" --body "本文です"
```

## 補足

- `token.json` にはアクセストークン情報が保存されます。公開リポジトリへはコミットしないでください。
- 送信元は認証した Gmail アカウントになります（`from_email="me"`）。
