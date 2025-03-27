# Telegram-Cities-Game-Automation
Автоматизированный соперник для игры "Города", работающий через ваш Telegram-аккаунт.

## 🚨 Перед запуском

**Обязательные настройки:**
1. В файле `config.py` укажите:
```python
RENDER_APP_URL = "ваш-рендер-проект.onrender.com"  # Для самопинга на сервере
```
Настройка сессии:
```python
# Для сервера:
SESSION_STRING = os.getenv("SESSION_STRING_SERVER")

# Для локального запуска:
SESSION_STRING = os.getenv("SESSION_STRING_TELETHON")
```
2. В файле `bot.py` задайте:
```python
CHAT_ID = -1002157100033    # ID основного чата
TOPIC_ID = 266173           # ID темы/ветки
GAME_BOT_ID = 1147621126    # ID игрового бота (@igravgorodabot)

CITIES_FILE = 'cities.txt'
REPORT_CHAT_ID = -4697646215  # ID группы для отчетов
MOSCOW_TZ = pytz.timezone('Europe/Moscow')
```

## 🌟 Особенности

- 🔐 Работает только в указанном чате/ветке
- 🔒 Команды доступны только владельцу аккаунта
- 🛡 Самопинг для работы на бесплатных серверах
- 🌆 Начальная база из 1073 городов России
- 🏙 **Автообучаемая база городов**
  Бот автоматически пополняет базу из:
    - Угаданных соперниками городов
    - Ответов игрового бота
    - Конфликтных ситуаций в игре
- 📈 **Динамическое обновление**
  База постоянно расширяется и сохраняется в файле [cities.txt](cities.txt):
    - Автоматическая сортировка по алфавиту
    - Оптимизация для быстрого поиска
    - Ежедневные отчеты в Telegram и перезапись файла в UTF-8
- 🚀 **Умная игра**
  Два режима работы:
    - **Спидран**: мгновенные ответы + авто-перезапуск игры
    - **Спокойно**: задержка ответов 2.5-5.5 сек + ручной перезапуск
- 🛠 **Технологии**
  - Множества вместо списков для O(1) поиска
  - Автоматическая сортировка после каждых 100 новых городов
  - Защита от дубликатов и ошибок формата

## ⚠️ Совместимость

- Бот разработан для [@igravgorodabot](https://t.me/igravgorodabot)
- Для других ботов потребуется:\
    1\. Изменить `GAME_BOT_ID` в коде\
    2\. Переписать регулярные выражения\
    3\. Адаптировать логику парсинга

## 🛠️ Требования

- Python 3.9+
- [requirements.txt](requirements.txt)
- Telegram API ключи
- Файл [cities.txt](cities.txt) с городами

**Важно!** Файл cities.txt должен быть в кодировке UTF-8.  
Если возникают проблемы с кодировкой:  
[Конвертер в UTF-8](https://subtitletools.com/convert-text-files-to-utf8-online)

**Формат файла cities.txt** (поддерживается автоматическое создание и обновление)**:**\
москва\
санкт-петербург\
нью-йорк\
киев\
...

## 📋 Команды управления

| Команда           | Описание                          | Доступность       |
|-------------------|-----------------------------------|-------------------|
| `/bot_on`         | Активировать бота                 | Только владелец   |
| `/bot_off`        | Деактивировать бота               | Только владелец   |
| `/mode спидран`   | Режим мгновенных ответов          | Только владелец   |
| `/mode спокойно`  | Режим с задержкой ответов         | Только владелец   |
| `/cities`         | Показать количество городов в базе| Только владелец   |

## 📄 Лицензия

[License](LICENSE) - Полный текст лицензии доступен в файле LICENSE

---

**Автор**: [@andranik_amrahyan](https://t.me/andranik_amrahyan)
