from config import load_config
from line_client import send_text_message
from slack_client import fetch_latest_messages
from summarizer import summarize_messages


def main() -> None:
    config = load_config()

    print("Slack からメッセージを取得中...")
    messages = fetch_latest_messages(
        token=config.slack_bot_token,
        channel_id=config.slack_channel_id,
        limit=10,
    )
    print(f"{len(messages)} 件取得しました")

    print("AI で要約中...")
    summary = summarize_messages(config.openai_api_key, messages)

    line_message = f"【Slack要約】\n\n{summary}"
    print("LINE に送信中...")
    send_text_message(
        access_token=config.line_channel_access_token,
        user_id=config.line_user_id,
        text=line_message,
    )
    print("送信完了")


if __name__ == "__main__":
    main()
