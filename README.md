# Google Meet 参加リンク生成スクリプト

`create_meet_link.py` は Google Calendar API を使って予定を作成し、Google Meet の参加リンクを生成します。

## 1. 事前準備

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. `Google Calendar API` を有効化
3. `OAuth 同意画面` を設定
4. 認証情報で `OAuth クライアント ID (デスクトップアプリ)` を作成
5. ダウンロードした JSON をこのフォルダに `credentials.json` として配置

## 2. インストール

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. 実行

### 最小実行（5分後開始 / 30分）

```bash
python create_meet_link.py
```

### 日時・参加者を指定

```bash
python create_meet_link.py ^
  --title "週次ミーティング" ^
  --start 2026-04-20T10:00 ^
  --duration-minutes 45 ^
  --timezone Asia/Tokyo ^
  --attendee user1@example.com ^
  --attendee user2@example.com
```

初回実行時はブラウザで Google 認可画面が開き、完了後に `token.json` が作成されます。

## 主なオプション

- `--title`: 予定タイトル
- `--start`: 開始日時（ISO形式）
- `--duration-minutes`: 会議時間（分）
- `--timezone`: タイムゾーン（例: `Asia/Tokyo`）
- `--attendee`: 招待先メール（複数指定可）
- `--credentials`: OAuth JSON のパス（既定: `credentials.json`）
- `--token`: トークン保存パス（既定: `token.json`）
