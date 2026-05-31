import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(
            f"環境変数 {name} が設定されていません。.env.example を参考に .env を作成してください。"
        )
    return value


class Config:
    WEBHOOK_URL: str = _require_env("WEBHOOK_URL")
    WEBHOOK_USERNAME: str = os.getenv("WEBHOOK_USERNAME", "通知Bot").strip()
    CRON_SCHEDULE: str | None = os.getenv("CRON_SCHEDULE", "").strip() or None
    CRON_MESSAGE: str = os.getenv("CRON_MESSAGE", "定期通知です。").strip()
