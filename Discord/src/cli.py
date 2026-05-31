"""コマンドラインから Webhook 経由で通知を送信する"""

import sys

from config import Config
from notifier import send_notification


def send_message(message: str) -> bool:
    try:
        send_notification(
            Config.WEBHOOK_URL,
            message,
            username=Config.WEBHOOK_USERNAME,
            embed_title="通知",
            embed_footer="CLI から送信",
        )
        print("通知を送信しました:", message)
        return True
    except Exception as exc:
        print("送信失敗:", exc)
        return False


def interactive_mode() -> None:
    print("手動通知モード（空 Enter で終了）")
    print("※ 定期通知の停止は scheduler.py を動かしているターミナルで Ctrl+C")
    print("   または stop.bat を実行してください")
    while True:
        try:
            message = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了しました")
            break

        if not message or message in ("^C", "exit", "quit", "終了"):
            print("終了しました")
            break

        send_message(message)


def main() -> None:
    message = " ".join(sys.argv[1:]).strip()
    if message:
        sys.exit(0 if send_message(message) else 1)
    interactive_mode()


if __name__ == "__main__":
    main()
