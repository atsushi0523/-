import argparse
import json
import os
from datetime import datetime, timedelta, timezone

import requests


ZOOM_OAUTH_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE_URL = "https://api.zoom.us/v2"


def load_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable '{name}' is required.")
    return value


def get_access_token() -> str:
    account_id = load_env("ZOOM_ACCOUNT_ID")
    client_id = load_env("ZOOM_CLIENT_ID")
    client_secret = load_env("ZOOM_CLIENT_SECRET")

    response = requests.post(
        ZOOM_OAUTH_URL,
        params={"grant_type": "account_credentials", "account_id": account_id},
        auth=(client_id, client_secret),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def create_meeting(
    access_token: str,
    user_id: str,
    topic: str,
    start_time_utc: datetime,
    duration_minutes: int,
) -> dict:
    url = f"{ZOOM_API_BASE_URL}/users/{user_id}/meetings"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "topic": topic,
        "type": 2,
        "start_time": start_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration_minutes,
        "timezone": "UTC",
        "settings": {
            "join_before_host": False,
            "waiting_room": True,
            "host_video": True,
            "participant_video": True,
            "approval_type": 0,
        },
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    response.raise_for_status()
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Zoom meeting and print ID, passcode, and join URL."
    )
    parser.add_argument("--user-id", default="me", help="Zoom user ID or email. Default: me")
    parser.add_argument("--topic", default="API Created Meeting", help="Meeting topic")
    parser.add_argument(
        "--start-in-minutes",
        type=int,
        default=10,
        help="How many minutes from now to schedule the meeting",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Meeting duration in minutes",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_time_utc = datetime.now(timezone.utc) + timedelta(minutes=args.start_in_minutes)

    token = get_access_token()
    meeting = create_meeting(
        access_token=token,
        user_id=args.user_id,
        topic=args.topic,
        start_time_utc=start_time_utc,
        duration_minutes=args.duration,
    )

    print("Meeting created successfully")
    print(f"Meeting ID     : {meeting.get('id')}")
    print(f"Passcode       : {meeting.get('password')}")
    print(f"Join URL       : {meeting.get('join_url')}")
    print(f"Start URL      : {meeting.get('start_url')}")


if __name__ == "__main__":
    main()
