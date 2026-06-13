from datetime import datetime, timezone

import requests

SLACK_API_BASE = "https://slack.com/api"


def fetch_latest_messages(token: str, channel_id: str, limit: int = 10) -> list[dict]:
    response = requests.get(
        f"{SLACK_API_BASE}/conversations.history",
        headers={"Authorization": f"Bearer {token}"},
        params={"channel": channel_id, "limit": limit},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Slack API エラー: {data.get('error', 'unknown')}")

    messages = []
    for msg in data.get("messages", []):
        if msg.get("subtype") in ("channel_join", "channel_leave"):
            continue
        ts = float(msg.get("ts", 0))
        posted_at = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        messages.append(
            {
                "user": msg.get("user", "unknown"),
                "text": msg.get("text", "").strip(),
                "posted_at": posted_at,
            }
        )

    messages.reverse()
    return messages
