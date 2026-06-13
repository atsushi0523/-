import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    slack_bot_token: str
    slack_channel_id: str
    openai_api_key: str
    line_channel_access_token: str
    line_user_id: str


def load_config() -> Config:
    required = {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "SLACK_CHANNEL_ID": os.getenv("SLACK_CHANNEL_ID"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LINE_CHANNEL_ACCESS_TOKEN": os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),
        "LINE_USER_ID": os.getenv("LINE_USER_ID"),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ValueError(f"環境変数が未設定です: {', '.join(missing)}")

    return Config(
        slack_bot_token=required["SLACK_BOT_TOKEN"],
        slack_channel_id=required["SLACK_CHANNEL_ID"],
        openai_api_key=required["OPENAI_API_KEY"],
        line_channel_access_token=required["LINE_CHANNEL_ACCESS_TOKEN"],
        line_user_id=required["LINE_USER_ID"],
    )
