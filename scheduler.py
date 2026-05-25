from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from config import TIMEZONE, MORNING_HOUR, MORNING_MINUTE
from db import get_all_active_users
from horoscope import generate_general_horoscope, generate_personal_block, ZODIAC_SIGNS

async def send_horoscopes(bot, group_chat_id):
    users = get_all_active_users()
    if not users:
        return

    # Группируем по знаку
    by_sign = {}
    for u in users:
        sign = u['sign']
        by_sign.setdefault(sign, []).append(u)

    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).strftime("%d.%m.%Y")

    for sign_en, users_list in by_sign.items():
        sign_ru = ZODIAC_SIGNS[sign_en]
        msg = f"♉ {sign_ru}\n\n"
        # Общий гороскоп для знака
        msg += "🌠 Небесная канцелярия:\n"
        msg += generate_general_horoscope(sign_en, today) + "\n\n"

        # Персональные блоки
        for u in users_list:
            msg += "─────────────────\n"
            msg += f"👤 {u['first_name']}\n"
            msg += generate_personal_block(u, today) + "\n\n"

        # Отправляем сообщение в группу
        try:
            await bot.send_message(chat_id=group_chat_id, text=msg.strip())
        except Exception as e:
            print(f"Failed to send message for {sign_ru}: {e}")

def setup_scheduler(bot, group_chat_id):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(
        send_horoscopes,
        trigger=CronTrigger(hour=MORNING_HOUR, minute=MORNING_MINUTE),
        args=[bot, group_chat_id],
        id="morning_horoscope"
    )
    return scheduler
