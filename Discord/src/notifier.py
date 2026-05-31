from datetime import UTC, datetime

import requests


def send_notification(
    webhook_url: str,
    message: str,
    *,
    username: str | None = None,
    embed_title: str = "通知",
    embed_footer: str | None = None,
    use_embed: bool = True,
) -> None:
    payload: dict = {}

    if username:
        payload["username"] = username

    if use_embed:
        embed: dict = {
            "title": embed_title,
            "description": message,
            "color": 0x5865F2,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if embed_footer:
            embed["footer"] = {"text": embed_footer}
        payload["embeds"] = [embed]
    else:
        payload["content"] = message

    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
