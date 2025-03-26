from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import config

# Укажите ваши данные API
API_ID = config.API_ID
API_HASH = config.API_HASH
PHONE_NUMBER = "+37493459113"

async def create_session(session_file: str):
    # Создаем клиента с новой сессией (используем StringSession для генерации строки)
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    # Получаем строку сессии и сохраняем её в файл
    session_str = client.session.save()
    with open(session_file, 'w') as f:
        f.write(session_str)
    
    print(f"Новая сессия сохранена в {session_file}")
    print(f"\nСессионная строка {session_file}:")
    print(session_str)
    print("\nСохраните эту строку для дальнейшего использования.")
    await client.disconnect()

async def main():
    # Создаем сессию для тестов
    # await create_session('telethon_session.session')
    
    # Создаем сессию для сервера
    await create_session('server_telethon_session.session')

if __name__ == "__main__":
    asyncio.run(main())