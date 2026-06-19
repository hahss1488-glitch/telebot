# Telegram-бот учёта обслуживания автомобилей

Промышленный шаблон Telegram-бота на Python 3.11+, aiogram 3, SQLite, SQLAlchemy ORM, Alembic, APScheduler и python-dotenv.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните BOT_TOKEN
python bot.py
```

База данных создаётся автоматически в `data/telebot.db`, SQLite работает с WAL. Справочник замен при первом запуске заполняется базовыми элементами. Еженедельные резервные копии создаются в `backups/`, хранится 5 последних файлов.

## Архитектура

- `handlers/` — Telegram-сценарии и FSM.
- `services/` — бизнес-логика, отчёты, резервное копирование.
- `repositories/` — доступ к данным.
- `models.py` — ORM-модели.
- `database.py` — движок, сессии, WAL/FK и создание таблиц.
- `migrations/` — Alembic.
