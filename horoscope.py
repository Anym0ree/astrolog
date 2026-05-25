import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from datetime import datetime
import pytz
from config import TIMEZONE

openai.api_key = OPENAI_API_KEY

ZODIAC_SIGNS = {
    "aries": "Овен",
    "taurus": "Телец",
    "gemini": "Близнецы",
    "cancer": "Рак",
    "leo": "Лев",
    "virgo": "Дева",
    "libra": "Весы",
    "scorpio": "Скорпион",
    "sagittarius": "Стрелец",
    "capricorn": "Козерог",
    "aquarius": "Водолей",
    "pisces": "Рыбы"
}

def calculate_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    else:
        return "pisces"

def generate_general_horoscope(sign_en, date_str):
    sign_ru = ZODIAC_SIGNS[sign_en]
    day_of_week = get_day_of_week_ru()
    prompt = f"""Ты астролог-философ. Напиши общий гороскоп на {date_str} для знака {sign_ru}.
Сегодня {day_of_week}.
Стиль: вдохновляющий, немного поэтичный, без шаблонов.
Объём: 2-3 предложения.
Не используй обращений к конкретному человеку, только общая энергия знака."""
    return ask_gpt(prompt)

def generate_personal_block(user, date_str):
    sign_ru = ZODIAC_SIGNS[user['sign']]
    first_name = user['first_name']
    gender = "женщина" if user['gender'] == 'f' else "мужчина"
    gender_pronoun = "ей" if user['gender'] == 'f' else "ему"
    day_of_week = get_day_of_week_ru()

    prompt = f"""Ты дружелюбный астролог-наставник. Составь персональный блок гороскопа на {date_str} для {first_name} ({gender}).
Знак зодиака: {sign_ru}. День недели: {day_of_week}.

Ответ должен состоять из трёх частей, строго разделённых:
1. "Анализ дня:" — глубокий, тёплый разбор энергий дня именно для этого человека. 2-3 предложения, обращайся на "ты". Используй род существительных и местоимений, соответствующий полу ({gender_pronoun}).
2. "✅ Что делать:" — два конкретных, полезных совета.
3. "❌ Чего избегать:" — два предостережения.
4. "💬 Аффирмация:" — короткая позитивная фраза на день.

Ответ выдай без лишнего оформления, только текст блоков, начиная каждый с указанного заголовка."""
    return ask_gpt(prompt)

def generate_quick_tip(name, sign_ru, gender):
    pronoun = "ей" if gender == "женщина" else "ему"
    prompt = (
        f"Дай короткий, тёплый и полезный совет на ближайшее время для {name} ({gender}). "
        f"Знак зодиака: {sign_ru}. Совет должен быть в одном-двух предложениях, вдохновляющий, "
        f"с обращением на «ты» и родом {pronoun}. Без вступления, только сам совет."
    )
    return ask_gpt(prompt, temperature=0.8, max_tokens=80)

def ask_gpt(prompt, temperature=0.9, max_tokens=500):
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Ты полезный астрологический ассистент."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "🌫️ Звёзды сегодня затуманены, попробуй заглянуть позже."

def get_day_of_week_ru():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    return days[now.weekday()]
    
