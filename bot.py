# «Telegram-Cities-Game-Automation»
# Автоматизированный соперник для игры "Города", работающий через ваш Telegram-аккаунт.

# ДО ЗАПУСКА БОТА:
# RENDER_APP_URL в config.py
# SESSION_STRING = os.getenv("SESSION_STRING_SERVER") в bot.py | Если запуск в сервере, иначе "SESSION_STRING_TELETHON"
# Переменные в bot.py

from telethon import TelegramClient, events, sessions
import asyncio
import os
import re
import random
from dotenv import load_dotenv
import logging
import colorlog
from flask import Flask
import threading
import aiohttp
import config
from datetime import datetime, timedelta
import pytz

# Фильтрация лишних логов
class OutputFilter:
    def __init__(self, original_output):
        self.original_output = original_output

    def write(self, text):
        if "Got difference for" not in text:
            self.original_output.write(text)

    def flush(self):
        self.original_output.flush()

import sys
sys.stdout = OutputFilter(sys.stdout)
sys.stderr = OutputFilter(sys.stderr)

# Настройка логирования
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
SESSION_STRING = os.getenv("SESSION_STRING_SERVER")
API_ID = config.API_ID
API_HASH = config.API_HASH

# Инициализация клиента Telethon
client = TelegramClient(
    sessions.StringSession(SESSION_STRING),
    API_ID,
    API_HASH,
    system_version="4.16.30-vxCUSTOM"
)

# Настройки чата
CHAT_ID = -1002157100033       # ID основного чата (https://t.me/Family_Worlds/1)
TOPIC_ID = 266173              # ID темы/ветки чата (https://t.me/Family_Worlds/266173)
GAME_BOT_ID = 1147621126       # ID игрового бота (@igravgorodabot)

CITIES_FILE = 'cities.txt'
REPORT_CHAT_ID = -1002571801416  # ID группы для отчетов
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Состояние бота
class State:
    is_active = False
    used_cities = set()
    current_letter = None
    last_city = None
    cities = {}  # { 'А': {'город1', 'город2'}, ... }
    discovered_cities = set()
    mode = "спокойно"  # "спидран" | "спокойно"
    my_user_id = None

# Загрузка городов из файла
def load_cities():
    State.cities.clear()
    try:
        with open(CITIES_FILE, 'r+', encoding='utf-8') as f:
            existing = {line.strip().lower() for line in f.readlines()}
            State.discovered_cities = existing.copy()
            
            for city in existing:
                if city:
                    first_letter = city[0].upper()
                    if first_letter not in State.cities:
                        State.cities[first_letter] = set()
                    State.cities[first_letter].add(city)
    except FileNotFoundError:
        open(CITIES_FILE, 'w').close()

load_cities()

# Инициализация Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/ping")
def ping():
    return "pong", 200

def run_web_server():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_web_server, daemon=True).start()

async def self_ping():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{config.RENDER_APP_URL}/ping") as resp:
                    logger.info(f"Self-ping status: {resp.status}")
        except Exception as e:
            logger.error(f"Self-ping error: {str(e)}")
        await asyncio.sleep(300)

async def save_new_city(city: str):
    normalized = city.strip().lower()
    if not normalized:
        return
    
    if normalized not in State.discovered_cities:
        try:
            with open(CITIES_FILE, 'a', encoding='utf-8') as f:
                f.write(normalized + '\n')
            State.discovered_cities.add(normalized)

            # Добавляем город в использованные
            State.used_cities.add(normalized)
            
            # Обновляем State.cities
            first_letter = normalized[0].upper()
            if first_letter not in State.cities:
                State.cities[first_letter] = []
            if normalized not in State.cities[first_letter]:
                State.cities[first_letter].append(normalized)
                logger.info(f"✅ Добавлен новый город: {normalized}")
        except Exception as e:
            logger.error(f"Ошибка сохранения города: {str(e)}")

@client.on(events.NewMessage(
    from_users=GAME_BOT_ID,
    chats=CHAT_ID
))
async def game_handler(event):
    text = event.raw_text
    # logger.info(f"Received message: {text}")

    # Всегда парсим города независимо от активности бота
    city_patterns = [
        r'Город\s+"?([А-Яа-яЁё-]+)"?\s+(?:уже был|существует)',
        r'Верно,\s+([А-Яа-яЁё-]+)\s+существует',
        r'Первый город будет\s+([А-Яа-яЁё-]+)\.'
    ]
    
    for pattern in city_patterns:
        match = re.search(pattern, text)
        if match:
            city = match.group(1).lower()
            await save_new_city(city)
            break

    # Обработка остановки игры
    if "Игра остановлена" in text:
        State.used_cities.clear()
        State.current_letter = None
        State.last_city = None
        return

    # Обработка старта новой игры
    if "Первый город будет" in text:
        State.used_cities.clear()
        State.current_letter = None
        State.last_city = None
        logger.info("🔄 Сброс состояния для новой игры")

        if not State.is_active:
            return
        
        letter_match = re.search(r'на букву "([А-Яа-я])"', text)
        if letter_match:
            State.current_letter = letter_match.group(1).upper()
            await send_next_city(event.chat_id)
        return

    if not State.is_active:
        return

    # Обработка ошибок с обновлением буквы
    if any(phrase in text for phrase in ["уже был", "не начинается с буквы"]):
        # Ищем новую букву в сообщении об ошибке
        new_letter_match = re.search(r'с буквы\s*"([А-Яа-я])"', text)
        if new_letter_match:
            new_letter = new_letter_match.group(1).upper()
            logger.info(f"🔄 Обновляем букву на {new_letter} из сообщения об ошибке")
            State.current_letter = new_letter
        
        # Если ошибка "уже был" - находим проблемный город в сообщении
        if "уже был" in text:
            city_match = re.search(r'Город\s+"?([А-Яа-яЁё-]+)"?\s+уже был', text)
            if city_match:
                invalid_city = city_match.group(1).strip().lower()
                State.used_cities.add(invalid_city)
                logger.info(f"🚫 Добавлен конфликтный город в used_cities: {invalid_city}")
        
        await send_next_city(event.chat_id)
        return

    # Поиск новой буквы в процессе игры
    letter_match = re.search(r'на (?:букву|начинающийся с буквы) "([А-Яа-я])"', text)
    if letter_match:
        State.current_letter = letter_match.group(1).upper()
        await send_next_city(event.chat_id)

async def send_next_city(chat_id):
    if not State.current_letter:
        return

    # Задержка для режима "спокойно"
    if State.mode == "спокойно":
        delay = random.uniform(2.5, 5.5)
        logger.info(f"🕒 Режим 'спокойно': ждем {delay:.1f} сек.")
        await asyncio.sleep(delay)

    available = State.cities.get(State.current_letter, set())
    unused = available - State.used_cities  # Быстрая разница множеств
    
    if unused:
        city = random.choice(list(unused)) if State.mode == "спокойно" else next(iter(unused))
        try:
            await client.send_message(
                entity=chat_id,
                message=city.capitalize(),
                reply_to=TOPIC_ID
            )
            State.used_cities.add(city)
            State.last_city = city
        except Exception as e:
            logger.error(f"Error sending city: {str(e)}")
    else:
        if State.mode == "спидран":
            await client.send_message(chat_id, '/stop@igravgorodabot', reply_to=TOPIC_ID)
            await asyncio.sleep(1)
            await client.send_message(chat_id, '/start@igravgorodabot', reply_to=TOPIC_ID)
        else:
            logger.info("🔇 Режим 'спокойно': не перезапускаем игру")

# Ежедневный отчет
async def daily_report():
    while True:
        now = datetime.now(MOSCOW_TZ)
        target_time = now.replace(hour=23, minute=59, second=0, microsecond=0)
        
        if now > target_time:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        try:
            if os.path.exists(CITIES_FILE):
                total = len(State.discovered_cities)
                await client.send_file(
                    entity=REPORT_CHAT_ID,
                    file=CITIES_FILE,
                    caption=f"📅 Ежедневный отчет городов ({datetime.now().strftime('%d.%m.%Y')})\n"
                            f"📊 Всего в базе: {total} городов",
                    allow_cache=False,
                    silent=True
                )
                logger.info("📤 Отчет успешно отправлен")
        except Exception as e:
            logger.error(f"Ошибка отправки отчета: {str(e)}")

@client.on(events.NewMessage(chats=CHAT_ID, pattern='/mode спидран'))
async def set_speedrun_mode(event):
    if event.sender_id != State.my_user_id:
            return
    State.mode = "спидран"
    await event.reply('🚀 Режим "спидран" активирован: быстрые ответы, авто-перезапуск')

@client.on(events.NewMessage(chats=CHAT_ID, pattern='/mode спокойно'))
async def set_quiet_mode(event):
    if event.sender_id != State.my_user_id:
            return
    State.mode = "спокойно"
    await event.reply('☕ Режим "спокойно" активирован: задержка ответов, ручной перезапуск')

@client.on(events.NewMessage(chats=CHAT_ID, pattern='/cities'))
async def get_cities_count(event):
    if event.sender_id != State.my_user_id:
        return
    count = len(State.discovered_cities)
    await event.reply(f"🏙 Всего городов в базе: {count}", reply_to=TOPIC_ID)

@client.on(events.NewMessage(chats=CHAT_ID, pattern='/bot_on'))
async def activate_bot(event):
    if event.sender_id != State.my_user_id:
            return
    State.is_active = True
    await event.reply('✅ Бот активирован')

@client.on(events.NewMessage(chats=CHAT_ID, pattern='/bot_off'))
async def deactivate_bot(event):
    if event.sender_id != State.my_user_id:
            return
    State.is_active = False
    await event.reply('⛔ Бот деактивирован')

async def main():
    await client.start()
    me = await client.get_me()
    State.my_user_id = me.id
    logger.info(f"Bot started! User ID: {State.my_user_id}")
    
    asyncio.create_task(self_ping())
    asyncio.create_task(daily_report())
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
