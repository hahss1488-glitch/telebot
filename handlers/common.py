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
    await message.answer("Бот учёта обслуживания автомобилей готов к работе. Выберите действие в меню.", reply_markup=MAIN_MENU)
