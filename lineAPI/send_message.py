import json
import os
import sys
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

PUSH_URL = "https://api.line.me/v2/bot/message/push"


def send_text_message(*, channel_access_token: str, to: str, text: str) -> dict:
    """LINE Messaging API でプッシュメッセージ（テキスト）を送る"""
    body = json.dumps(
        {"to": to, "messages": [{"type": "text", "text": text}]},
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        PUSH_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {channel_access_token}",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8")
        raise RuntimeError(
            f"LINE API error: {e.code} {e.reason}\n{detail}"
        ) from e


def main() -> None:
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    to = os.getenv("LINE_USER_ID")
    text = os.getenv("LINE_MESSAGE_TEXT", "こんにちは！テストメッセージです。")

    if not channel_access_token:
        print("環境変数 LINE_CHANNEL_ACCESS_TOKEN を設定してください。", file=sys.stderr)
        sys.exit(1)
    if not to:
        print("環境変数 LINE_USER_ID（送信先ID）を設定してください。", file=sys.stderr)
        sys.exit(1)

    result = send_text_message(
        channel_access_token=channel_access_token,
        to=to,
        text=text,
    )
    print("送信しました:", result)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        print(err, file=sys.stderr)
        sys.exit(1)
