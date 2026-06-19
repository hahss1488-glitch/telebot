from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import report_vehicles_keyboard
from repositories.service_records import ServiceRecordRepository
from services.report_service import ReportService

router = Router()

@router.message(F.text.in_({"Отчёт за сегодня", "📅 Отчёт за сегодня"}))
async def today_report(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    text, vehicles = await ReportService(ServiceRecordRepository(session)).today()
    await message.answer(text + "\n\nМашины с задачами сегодня:", reply_markup=report_vehicles_keyboard(vehicles, "today"))

@router.message(F.text.in_({"Отчёт за месяц", "📊 Отчёт за месяц"}))
async def month_report(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await send_month_report(message, session, 0)

@router.callback_query(F.data.startswith("report:month:"))
async def month_report_page(call: CallbackQuery, session: AsyncSession) -> None:
    await send_month_report(call.message, session, int(call.data.split(":")[-1]))
    await call.answer()

async def send_month_report(message: Message, session: AsyncSession, page: int) -> None:
    text, vehicles = await ReportService(ServiceRecordRepository(session)).month()
    await message.answer(text + "\n\nМашины с задачами за месяц:", reply_markup=report_vehicles_keyboard(vehicles, "month", page=page, page_size=5))
