# -*- coding: utf-8 -*-
"""
Google カレンダー API で予定を追加する（サービスアカウント認証）。

前提:
  - Google Cloud で Calendar API を有効化していること
  - このスクリプトと同じフォルダに service_account.json を置くこと
  - 他人のカレンダーに書き込む場合は、そのカレンダーを
    サービスアカウントの client_email に「予定の変更」権限で共有すること
  - 環境変数 CALENDAR_ID で対象カレンダーを指定可能（未指定時は primary）
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

# 予定の作成・変更に必要なスコープ
SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")
DEFAULT_CALENDAR_ID = "jingzhitiantian489@gmail.com"


def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def list_calendars() -> list[dict[str, Any]]:
    """
    サービスアカウントがアクセスできるカレンダー一覧を取得する。
    """
    service = get_calendar_service()
    # showHidden=True にしないと、primary 等が返らないケースがあるため明示する
    resp = service.calendarList().list(showHidden=True).execute()
    return resp.get("items", [])


def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    *,
    description: str = "",
    calendar_id: Optional[str] = None,
    time_zone: str = "Asia/Tokyo",
) -> Dict[str, Any]:
    """
    予定を1件作成する。

    :param summary: タイトル
    :param start: 開始日時（タイムゾーン付きを推奨）
    :param end: 終了日時
    :param description: 説明（任意）
    :param calendar_id: カレンダーID。未指定時は環境変数 CALENDAR_ID、それもなければ "primary"
    :param time_zone: カレンダー上のタイムゾーン（例: Asia/Tokyo）
    """
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start と end にはタイムゾーン付き datetime を指定してください。")

    cal_id = calendar_id or os.environ.get("CALENDAR_ID", "primary")

    body: Dict[str, Any] = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": time_zone,
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": time_zone,
        },
    }

    service = get_calendar_service()
    event = (
        service.events()
        .insert(calendarId=cal_id, body=body)
        .execute()
    )
    return event


def main() -> None:
    """
    入力した日付の当日に、入力した開始時刻〜終了時刻で入力したタイトルの予定を作成します。

    例:
      日付: 2026-03-30
      開始: 09:30
      終了: 10:30
      -> 2026-03-30 09:30〜10:30（Asia/Tokyo）
    """

    date_str = input("日付を入力してください（YYYY-MM-DD）: ").strip()
    start_time_str = input("開始時刻を入力してください（HH:MM 24時間 / HHも可）: ").strip()
    end_time_str = input("終了時刻を入力してください（HH:MM 24時間 / HHも可）: ").strip()
    title = input("予定のタイトルを入力してください: ").strip()

    if not date_str:
        raise ValueError("日付が未入力です。")
    if not start_time_str:
        raise ValueError("開始時刻が未入力です。")
    if not end_time_str:
        raise ValueError("終了時刻が未入力です。")
    if not title:
        raise ValueError("タイトルが未入力です。")

    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError("日付は YYYY-MM-DD 形式で入力してください。") from e

    # 入力は "HH:MM" または "HH" の両方を許容する
    # 例: 09:30 / 20
    def parse_time(s: str):
        for fmt in ("%H:%M", "%H"):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                pass
        raise ValueError("時刻は HH:MM 形式（例: 09:30）または HH（例: 20）で入力してください。")

    start_time = parse_time(start_time_str)
    end_time = parse_time(end_time_str)

    # 入力した日付の当日
    target_day = input_date

    # 予定時間
    tz = timezone(timedelta(hours=9))  # JST
    start = datetime(
        year=target_day.year,
        month=target_day.month,
        day=target_day.day,
        hour=start_time.hour,
        minute=start_time.minute,
        second=0,
        microsecond=0,
        tzinfo=tz,
    )
    end = datetime(
        year=target_day.year,
        month=target_day.month,
        day=target_day.day,
        hour=end_time.hour,
        minute=end_time.minute,
        second=0,
        microsecond=0,
        tzinfo=tz,
    )

    if end <= start:
        raise ValueError("終了時刻は開始時刻より後にしてください（同日の範囲で入力）。")

    # 共有相手（サービスアカウント）のメールを表示して、共有設定の突合に使う
    with open(SERVICE_ACCOUNT_FILE, "r", encoding="utf-8") as f:
        sa_info = json.load(f)
    print("サービスアカウント client_email:", sa_info.get("client_email"))

    # 書き込み先 calendarId は固定（ターミナル入力なし）
    # CALENDAR_ID を環境変数で上書きしたい場合だけ変更されます。
    selected_calendar_id: str = os.environ.get("CALENDAR_ID", DEFAULT_CALENDAR_ID)

    print("作成予定:", start.isoformat(), "〜", end.isoformat())
    print("書き込み先 calendarId:", selected_calendar_id)

    event = create_event(
        summary=title,
        start=start,
        end=end,
        description="create_calendar_event.py から作成しました。",
        calendar_id=selected_calendar_id,
    )
    print("作成しました:", event.get("htmlLink"))
    print("event id:", event.get("id"))


if __name__ == "__main__":
    main()
