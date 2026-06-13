from __future__ import annotations

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import load_settings
from database import create_engine_and_session, init_db
from handlers import common, items, reports, service, vehicles
from middlewares.db import DbSessionMiddleware
from repositories.items import ReplacementItemRepository
from services.backup_service import BackupService
from utils.logging import setup_logging

async def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_dir, settings.log_level)
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is required. Copy .env.example to .env and fill BOT_TOKEN.")
    engine, session_factory = create_engine_and_session(settings.database_url)
    await init_db(engine)
    async with session_factory() as session:
        await ReplacementItemRepository(session).seed_defaults()
        await session.commit()
    backup_service = BackupService(settings.sqlite_path, settings.backup_dir)
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(backup_service.create_backup, "cron", day_of_week="sun", hour=3, minute=0, id="weekly_db_backup", replace_existing=True)
    scheduler.start()
    bot = Bot(settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(DbSessionMiddleware(session_factory))
    dp.include_routers(common.router, service.router, vehicles.router, items.router, reports.router)
    logging.getLogger(__name__).info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
