# -*- coding: utf-8 -*-
"""
Google Docs API を使って新規ドキュメントを作成し、指定テキストを挿入するサンプルです。

【事前準備（Google Cloud）】
1. Google Cloud Console（https://console.cloud.google.com/）でプロジェクトを作成または選択する。
2. 「API とサービス」→「ライブラリ」から「Google Docs API」を検索し、有効化する。
3. 「API とサービス」→「OAuth 同意画面」を設定する（個人利用ならテストモードで可）。
4. 「API とサービス」→「認証情報」→「認証情報を作成」→「OAuth クライアント ID」
   で「デスクトップアプリ」を作成し、JSON をダウンロードする。

【ライブラリのインストール】
  このフォルダで次を実行してください:
    pip install -r requirements.txt

【認証ファイル】
  OAuth クライアント JSON を、このスクリプトと同じフォルダに置き、
  OAUTH_CLIENT_FILENAME（既定: oauth_client.json）に合わせます。
  初回実行時にブラウザで認可し、TOKEN_FILENAME（既定: token.json）が自動作成されます。

実行すると新規 Google ドキュメントが作成され、指定した文字列が本文に挿入されます。
"""

import os
import sys
from pathlib import Path

# Google API クライアントと認証
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# ---------------------------------------------------------------------------
# ここを編集して、ドキュメントのタイトルと挿入するテキストを変えられます
# ---------------------------------------------------------------------------
DOCUMENT_TITLE = "API で作成したドキュメント"
INSERT_TEXT = "こんにちは。これは Python と Google Docs API で挿入したテキストです。"

# このスクリプトと同じフォルダに置く OAuth クライアント JSON のファイル名
OAUTH_CLIENT_FILENAME = "oauth_client.json"

# 実行後にアクセストークン/リフレッシュトークンを保存するファイル名
TOKEN_FILENAME = "token.json"

# スクリプトがあるフォルダ（この直下に JSON を置くと自動検出されます）
_SCRIPT_DIR = Path(__file__).resolve().parent


# Docs API で必要な権限（ドキュメントの作成・編集）
SCOPES = ("https://www.googleapis.com/auth/documents",)


def get_runtime_content(default_title: str, default_text: str) -> tuple[str, str]:
    """
    実行時にタイトルと本文を受け取ります。

    何も入力されなかった場合は既定値を使います。
    """
    print("ドキュメントのタイトルと本文を入力できます。")
    print("そのまま Enter を押すと既定値を使います。")

    title_input = input(f"タイトル [{default_title}]: ").strip()
    text_input = input(f"本文 [{default_text}]: ").strip()

    title = title_input if title_input else default_title
    text = text_input if text_input else default_text
    return title, text


def build_docs_service():
    """
    OAuth（ユーザー認証）で Google Docs API 用のサービスオブジェクトを返します。
    """
    oauth_client_path = _SCRIPT_DIR / OAUTH_CLIENT_FILENAME
    token_path = _SCRIPT_DIR / TOKEN_FILENAME

    credentials = None
    if token_path.is_file():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.isfile(oauth_client_path):
                raise FileNotFoundError(
                    f"OAuth クライアント JSON が見つかりません: {oauth_client_path}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(oauth_client_path),
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        token_path.write_text(credentials.to_json(), encoding="utf-8")

    # v1 が現在の Docs API バージョンです
    return build("docs", "v1", credentials=credentials, cache_discovery=False)


def create_document(service, title: str) -> str:
    """
    タイトル付きの新規ドキュメントを作成し、documentId を返します。

    Args:
        service: build_docs_service() で取得したサービス
        title: ドキュメントのタイトル

    Returns:
        作成されたドキュメントの documentId（URL 等で使う ID）
    """
    # documents().create で空のドキュメントが Cloud 上に作成されます
    body = {"title": title}
    doc = service.documents().create(body=body).execute()
    document_id = doc.get("documentId")
    if not document_id:
        raise RuntimeError("API の応答に documentId が含まれていません。")
    return document_id


def insert_text_at_start(service, document_id: str, text: str) -> None:
    """
    ドキュメントの先頭付近にテキストを挿入します。

    空のドキュメントでは、先頭に改行 1 文字分の領域があるため、
    通常は index 1 の位置に挿入すると文頭に文字列が入ります。

    Args:
        service: Docs API サービス
        document_id: 対象ドキュメントの ID
        text: 挿入する文字列
    """
    if not text:
        raise ValueError("挿入するテキストが空です。INSERT_TEXT を確認してください。")

    # batchUpdate で複数リクエストをまとめて送れます（ここでは insertText のみ）
    requests_body = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": text,
                }
            }
        ]
    }
    service.documents().batchUpdate(
        documentId=document_id, body=requests_body
    ).execute()


def main() -> None:
    """
    ドキュメント新規作成 → テキスト挿入まで一連の流れを実行します。
    """
    # 実行時入力（未入力なら既定値）からタイトルと本文を取得
    try:
        title, text_to_insert = get_runtime_content(DOCUMENT_TITLE, INSERT_TEXT)
    except (EOFError, KeyboardInterrupt):
        print("\n入力が中断されたため終了します。", file=sys.stderr)
        sys.exit(1)

    try:
        service = build_docs_service()
    except FileNotFoundError as e:
        print("【エラー】認証ファイル:", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("【エラー】API サービスの初期化に失敗しました:", e, file=sys.stderr)
        sys.exit(1)

    try:
        document_id = create_document(service, title)
        print(f"ドキュメントを作成しました。documentId: {document_id}")

        insert_text_at_start(service, document_id, text_to_insert)
        print("指定したテキストを挿入しました。")

        # ブラウザで開くための URL（認証したユーザーのドライブに保存されます）
        url = f"https://docs.google.com/document/d/{document_id}/edit"
        print(f"編集用 URL: {url}")

    except HttpError as e:
        # API が 4xx/5xx を返したとき（権限不足、API 未有効化など）
        print("【エラー】Google Docs API のリクエストが失敗しました。", file=sys.stderr)
        print(f"  ステータス: {e.resp.status if e.resp else '不明'}", file=sys.stderr)
        print(f"  詳細: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print("【エラー】入力値:", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("【エラー】予期しない問題が発生しました:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
