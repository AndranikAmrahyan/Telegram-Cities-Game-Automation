from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Получаем значения из переменных окружения
API_ID = int(os.getenv("API_ID"))  # Твой API ID
API_HASH = os.getenv("API_HASH")  # Твой API HASH

# Сервер на Render
RENDER_APP_URL = os.getenv("RENDER_APP_URL")  # Ставь свою ссылку с Render. Пример: https://your_app.onrender.com
