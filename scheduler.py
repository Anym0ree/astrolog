from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from config import TIMEZONE, MORNING_HOUR, MORNING_MINUTE
from db import get_all_active_users, get_all_groups, remove_group
from horoscope import generate_general_horoscope, generate_personal_block, ZODIAC_SIGNS
import logging

logger = logging.getLogger(__name__)

async def send_horoscopes(bot):
    users = get_all_active_users()
    if not users:
        return

    by_sign = {}
    for u in users:
        sign = u['sign']
        by_sign.setdefault(sign, []).append(u)

    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).strftime("%d.%m.%Y")

    groups = get_all_groups()
    if not groups:
        from config import GROUP_CHAT_ID
        if GROUP_CHAT_ID:
            groups = [GROUP_CHAT_ID]
        else:
            logger.warning("Нет сохранённых групп и не задан GROUP_CHAT_ID")
            return

    for group_id in groups:
        for sign_en, users_list in by_sign.items():
            sign_ru = ZODIAC_SIGNS[sign_en]
            msg = f"♉ {sign_ru}\n\n"
            msg += "🌠 Небесная канцелярия:\n"
            msg += generate_general_horoscope(sign_en, today) + "\n\n"

            for u in users_list:
                msg += "─────────────────\n"
                msg += f"👤 {u['first_name']}\n"
                msg += generate_personal_block(u, today) + "\n\n"

            try:
                await bot.send_message(chat_id=group_id, text=msg.strip())
            except Exception as e:
                logger.error(f"Ошибка отправки в чат {group_id}: {e}")
                if "chat not found" in str(e).lower():
                    remove_group(group_id)

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(
        send_horoscopes,
        trigger=CronTrigger(hour=MORNING_HOUR, minute=MORNING_MINUTE),
        args=[bot],
        id="morning_horoscope"
    )
    return scheduler
