import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
if GROUP_CHAT_ID:
    GROUP_CHAT_ID = int(GROUP_CHAT_ID)
else:
    GROUP_CHAT_ID = None
TIMEZONE = os.getenv("MOSCOW_TIMEZONE", "Europe/Moscow")
MORNING_HOUR = int(os.getenv("MORNING_HOUR", 9))
MORNING_MINUTE = int(os.getenv("MORNING_MINUTE", 0))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
