import config
import os
import argparse
from telethon import TelegramClient, sessions
from telethon.tl.types import Channel, Chat, User

SESSION_STRING = os.getenv("SESSION_STRING_TELETHON")
client = TelegramClient(
    sessions.StringSession(SESSION_STRING),
    config.API_ID,
    config.API_HASH
)

async def print_chat_info(dialog):
    """Выводит информацию о чате в удобном формате"""
    chat_type = ""
    if isinstance(dialog.entity, Channel):
        chat_type = "Канал" if dialog.entity.broadcast else "Супергруппа"
    elif isinstance(dialog.entity, Chat):
        chat_type = "Группа"
    elif isinstance(dialog.entity, User):
        chat_type = "Личный чат"
    
    print("\n" + "=" * 40)
    print(f"Название: {dialog.name}")
    print(f"ID: {dialog.id}")
    print(f"Тип: {chat_type}")
    
    if hasattr(dialog.entity, 'username') and dialog.entity.username:
        print(f"Ссылка: https://t.me/{dialog.entity.username}")
    print("=" * 40)

async def main(args):
    async with client:
        async for dialog in client.iter_dialogs():
            # Режим поиска по ID
            if args.id and dialog.id == args.id:
                await print_chat_info(dialog)
                return
            
            # Режим поиска по названию
            if args.name and args.name.lower() in dialog.name.lower():
                await print_chat_info(dialog)
                if not args.all:
                    return
            
            # Режим показа всех чатов
            if args.all:
                await print_chat_info(dialog)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Поиск Telegram чатов")
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument("--id", type=int, 
                      help="Поиск чата по точному ID")
    group.add_argument("--name", type=str,
                      help="Поиск по части названия (регистронезависимо)")
    group.add_argument("--all", action="store_true",
                      help="Показать все доступные чаты")
    
    return parser.parse_args()

if __name__ == "__main__":
    import asyncio
    args = parse_arguments()
    
    if not any([args.id, args.name, args.all]):
        print("Используйте один из параметров: --id, --name или --all")
    else:
        asyncio.run(main(args))