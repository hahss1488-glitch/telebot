from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.service_records import ServiceRecordRepository
from services.report_service import ReportService

router = Router()

@router.message(F.text == "Отчёт за сегодня")
async def today_report(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await message.answer(await ReportService(ServiceRecordRepository(session)).today_text())
