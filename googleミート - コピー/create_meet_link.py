import argparse
import datetime as dt
import uuid
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Meet リンク生成には Calendar API の conferenceData を使います。
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google Meet のミーティングを作成し、参加リンクを取得します。"
    )
    parser.add_argument("--title", default="オンラインミーティング", help="予定タイトル")
    parser.add_argument(
        "--start",
        help="開始日時 (例: 2026-04-20T10:00)。未指定の場合は現在時刻+5分。",
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=30,
        help="ミーティング時間(分)。デフォルト: 30",
    )
    parser.add_argument(
        "--timezone",
        default="Asia/Tokyo",
        help="タイムゾーン名 (例: Asia/Tokyo, UTC)",
    )
    parser.add_argument(
        "--attendee",
        action="append",
        default=[],
        help="招待メールアドレス。複数指定可。例: --attendee a@example.com",
    )
    parser.add_argument(
        "--credentials",
        default="credentials.json",
        help="OAuth クライアント情報(JSON)のパス",
    )
    parser.add_argument(
        "--token",
        default="token.json",
        help="認可トークン保存先。初回実行時に作成されます。",
    )
    return parser.parse_args()


def parse_start_time(start_text: str | None, tz_name: str) -> dt.datetime:
    tz = ZoneInfo(tz_name)
    if not start_text:
        return dt.datetime.now(tz) + dt.timedelta(minutes=5)

    # 例: 2026-04-20T10:00 / 2026-04-20T10:00:30
    parsed = dt.datetime.fromisoformat(start_text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def get_credentials(credentials_path: Path, token_path: Path) -> Credentials:
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def build_event_payload(
    title: str,
    start_time: dt.datetime,
    end_time: dt.datetime,
    timezone_name: str,
    attendees: List[str],
) -> dict:
    return {
        "summary": title,
        "start": {"dateTime": start_time.isoformat(), "timeZone": timezone_name},
        "end": {"dateTime": end_time.isoformat(), "timeZone": timezone_name},
        "attendees": [{"email": email} for email in attendees],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }


def main() -> None:
    args = parse_args()

    credentials_path = Path(args.credentials)
    token_path = Path(args.token)

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"OAuth クライアント情報が見つかりません: {credentials_path}\n"
            "Google Cloud Console から credentials.json を取得して同じフォルダに置いてください。"
        )

    start_time = parse_start_time(args.start, args.timezone)
    end_time = start_time + dt.timedelta(minutes=args.duration_minutes)
    event_body = build_event_payload(
        args.title, start_time, end_time, args.timezone, args.attendee
    )

    try:
        creds = get_credentials(credentials_path, token_path)
        service = build("calendar", "v3", credentials=creds)
        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event_body,
                conferenceDataVersion=1,
                sendUpdates="all" if args.attendee else "none",
            )
            .execute()
        )
    except HttpError as error:
        raise RuntimeError(f"Google API 呼び出しに失敗しました: {error}") from error

    meet_link = created_event.get("hangoutLink")
    if not meet_link:
        # API仕様上は conferenceData.entryPoints にもリンクが入る場合があります。
        entry_points = created_event.get("conferenceData", {}).get("entryPoints", [])
        meet_link = next(
            (ep.get("uri") for ep in entry_points if ep.get("entryPointType") == "video"),
            None,
        )

    print("ミーティングを作成しました。")
    print(f"タイトル: {created_event.get('summary')}")
    print(f"開始: {created_event.get('start', {}).get('dateTime')}")
    print(f"終了: {created_event.get('end', {}).get('dateTime')}")
    print(f"Meet 参加リンク: {meet_link or '取得できませんでした'}")
    print(f"Google カレンダー予定URL: {created_event.get('htmlLink')}")


if __name__ == "__main__":
    main()
