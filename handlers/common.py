from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import MAIN_MENU
from repositories.users import UserRepository

router = Router()

@router.message(CommandStart())
async def start(message: Message, session: AsyncSession) -> None:
    if message.from_user:
        await UserRepository(session).get_or_create(message.from_user)
    await message.answer("Бот учёта обслуживания автомобилей готов к работе.", reply_markup=MAIN_MENU)

@router.message(lambda m: m.text == "Настройки")
async def settings(message: Message) -> None:
    await message.answer("Настройки: заполните BOT_TOKEN в .env. Резервные копии выполняются еженедельно автоматически.")
