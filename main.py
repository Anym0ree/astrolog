import logging
from datetime import datetime, timedelta
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler
from config import BOT_TOKEN, GROUP_CHAT_ID, TIMEZONE
from db import init_db, save_user, get_user, save_group, remove_group
from horoscope import calculate_sign, ZODIAC_SIGNS, generate_quick_tip
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_states = {}

async def on_chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.my_chat_member
    if chat_member is None:
        return
    chat_id = chat_member.chat.id
    new_status = chat_member.new_chat_member.status

    if new_status in ("member", "administrator"):
        save_group(chat_id)
        logger.info(f"Бот добавлен в чат {chat_id}")
    elif new_status in ("left", "kicked"):
        remove_group(chat_id)
        logger.info(f"Бот удалён из чата {chat_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    user_states.pop(user_id, None)
    await update.message.reply_text(
        "Привет! Я астробот для вашего чата. Чтобы давать точные прогнозы, "
        "напиши свою дату рождения в формате ДД.ММ.ГГГГ (например, 12.07.1995)."
    )

async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    target_hour = 9
    target_minute = 0
    next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    delta = next_run - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes = remainder // 60
    time_str = f"{hours} ч. {minutes} мин." if hours else f"{minutes} мин."

    user_data = get_user(user_id)
    if user_data:
        sign_ru = ZODIAC_SIGNS[user_data['sign']]
        gender = "женщина" if user_data['gender'] == 'f' else "мужчина"
        tip = generate_quick_tip(user.first_name, sign_ru, gender)
    else:
        tip = ("✨ Совет дня: сделай паузу, выдохни и улыбнись. "
               "А чтобы получать персональные гороскопы — напиши мне в личку /start и укажи дату рождения.")

    text = (
        f"🌅 Следующий гороскоп выйдет через {time_str} (в 09:00 по МСК).\n\n"
        f"🪐 Пока лови небольшой совет:\n{tip}"
    )
    await context.bot.send_message(chat_id=chat_id, text=text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if update.effective_chat.type == "private":
        state = user_states.get(user_id)

        if state and state.get('state') == 'waiting_gender':
            if text.lower() in ('м', 'm', 'муж', 'парень'):
                gender = 'm'
            elif text.lower() in ('ж', 'f', 'жен', 'девушка'):
                gender = 'f'
            else:
                await update.message.reply_text("Пожалуйста, напиши «м» или «ж».")
                return

            birth_date = state['birth_date']
            sign = state['sign']
            first_name = update.effective_user.first_name
            save_user(user_id, first_name, birth_date, sign, gender)
            user_states.pop(user_id, None)
            await update.message.reply_text(
                "Отлично, запомнил! Теперь каждое утро в нашем чате тебя будет ждать личный гороскоп. Хорошего дня!"
            )
            return

        try:
            dt = datetime.strptime(text, "%d.%m.%Y")
            day, month = dt.day, dt.month
            sign = calculate_sign(day, month)
            user_states[user_id] = {
                'state': 'waiting_gender',
                'birth_date': text,
                'sign': sign
            }
            sign_ru = ZODIAC_SIGNS[sign]
            await update.message.reply_text(
                f"Принято! Ты — {sign_ru}. Теперь уточни последнее: ты парень или девушка? Напиши «м» или «ж»."
            )
        except ValueError:
            await update.message.reply_text("Неверный формат. Введи дату как ДД.ММ.ГГГГ (например, 12.07.1995).")

    else:
        # Запоминаем группу при любом сообщении в чате
        chat_id = update.effective_chat.id
        save_group(chat_id)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatMemberHandler(on_chat_member_update, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))

    scheduler = setup_scheduler(app.bot)
    scheduler.start()
    app.bot_data["scheduler"] = scheduler

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
