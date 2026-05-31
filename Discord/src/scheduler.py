"""定期通知スケジューラ（Webhook 経由）"""

import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import Config
from notifier import send_notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def _send_cron_notification() -> None:
    try:
        send_notification(
            Config.WEBHOOK_URL,
            Config.CRON_MESSAGE,
            username=Config.WEBHOOK_USERNAME,
            embed_title="定期通知",
            embed_footer="Webhook Notification",
        )
        logger.info("定期通知を送信しました: %s", Config.CRON_MESSAGE)
    except Exception:
        logger.exception("定期通知の送信に失敗")


def _build_trigger(schedule: str):
    parts = schedule.split()
    if len(parts) != 5:
        raise ValueError(f"無効な CRON_SCHEDULE: {schedule}")

    minute, hour, day, month, day_of_week = parts

    if schedule in ("* * * * *", "*/1 * * * *"):
        return IntervalTrigger(minutes=1)

    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
    )


def main() -> None:
    if not Config.CRON_SCHEDULE:
        print("CRON_SCHEDULE が未設定です。.env に cron 式を設定してください。")
        sys.exit(1)

    try:
        trigger = _build_trigger(Config.CRON_SCHEDULE)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    scheduler = BlockingScheduler()
    scheduler.add_job(_send_cron_notification, trigger=trigger, id="cron_notification")

    print("=" * 50)
    print("定期通知スケジューラを開始しました")
    print(f"  スケジュール: {Config.CRON_SCHEDULE}")
    print(f"  メッセージ  : {Config.CRON_MESSAGE}")
    print("  終了        : このウィンドウで Ctrl+C")
    print("              または stop.bat を実行")
    print("=" * 50)
    print()

    logger.info("初回通知を送信します...")
    _send_cron_notification()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print()
        logger.info("定期通知を終了しました")
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
