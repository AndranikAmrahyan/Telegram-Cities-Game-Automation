import config
import os
from telethon import TelegramClient, events, sessions
import asyncio

API_ID = config.API_ID
API_HASH = config.API_HASH
SESSION_STRING = os.getenv("SESSION_STRING_TELETHON")

client = TelegramClient(
    sessions.StringSession(SESSION_STRING),
    config.API_ID,
    config.API_HASH
)

async def get_user_id_by_username(username: str):
    try:
        user = await client.get_entity(username)
        print(f"ID пользователя {username}: {user.id}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def get_user_id_by_reply(chat):
    try:
        sent_message = await client.send_message(chat, "Ответьте на это сообщение, чтобы я мог получить ваш ID.")
        print(f"Сообщение отправлено в чат {chat}. Ожидаю ответа...")

        @client.on(events.NewMessage(incoming=True, chats=chat))
        async def handler(event):
            if event.is_reply and event.reply_to_msg_id == sent_message.id:
                print(f"ID пользователя, который ответил: {event.sender_id}")
                await client.disconnect()  # Отключаем клиент после получения ответа

        await client.run_until_disconnected()  # Ждем, пока клиент не отключится

    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main():
    await client.start()
    
    mode = input("Выберите режим (1 - по юзернейму, 2 - по ответу на сообщение): ")
    
    if mode == "1":
        username = input("Введите юзернейм (например, @username): ")
        await get_user_id_by_username(username)
    elif mode == "2":
        chat = input("Введите юзернейм или ID чата: ")
        chat = int(chat) if not chat.startswith("@") else chat
        await get_user_id_by_reply(chat)
    else:
        print("❌ Неверный режим.")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())