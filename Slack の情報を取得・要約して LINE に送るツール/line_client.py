import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def send_text_message(access_token: str, user_id: str, text: str) -> None:
    response = requests.post(
        LINE_PUSH_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "to": user_id,
            "messages": [{"type": "text", "text": text}],
        },
        timeout=30,
    )
    response.raise_for_status()

    if response.status_code != 200:
        raise RuntimeError(f"LINE API エラー: {response.status_code} {response.text}")
