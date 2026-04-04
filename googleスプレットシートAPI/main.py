import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build


# 必要に応じて環境変数で上書きできます
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "1fGarWUfXvZR60GcJUQ0AgPbVYRCPCfiJjZXqNXB1vAk")
TARGET_RANGE = os.getenv("GOOGLE_TARGET_RANGE", "シート1!A:C")

# スプレッドシートへの読み書き権限
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def append_rows(rows: List[List[str]]) -> None:
    """Googleスプレッドシートの末尾に複数行を追加する。"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    body = {"values": rows}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=TARGET_RANGE,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )

    print("書き込み成功:", result.get("updates", {}))


if __name__ == "__main__":
    # 送信したいデータ
    sample_rows = [
        ["2026-03-24", "りんご", "120"],
        ["2026-03-24", "みかん", "80"],
    ]
    append_rows(sample_rows)
