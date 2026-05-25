import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, GROUP_CHAT_ID
from db import init_db, save_user, get_user
from horoscope import calculate_sign, ZODIAC_SIGNS
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler (но для простоты используем два шага без библиотеки)
user_states = {}  # user_id -> {'state': 'waiting_gender', 'birth_date': ..., 'sign': ...}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Запускаем только в личке
    if update.effective_chat.type != "private":
        return
    user_id = update.effective_user.id
    user_states.pop(user_id, None)  # сброс
    await update.message.reply_text(
        "Привет! Я астробот для вашего чата. Чтобы давать точные прогнозы, "
        "напиши свою дату рождения в формате ДД.ММ.ГГГГ (например, 12.07.1995)."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Если это личка — обрабатываем регистрацию
    if update.effective_chat.type == "private":
        state = user_states.get(user_id)

        if state and state.get('state') == 'waiting_gender':
            # Ожидаем пол
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

        # Первый шаг — дата
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
        # В группах не отвечаем на сообщения, чтобы не шуметь
        pass

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Планировщик утренней рассылки
    scheduler = setup_scheduler(app.bot, GROUP_CHAT_ID)
    scheduler.start()

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
