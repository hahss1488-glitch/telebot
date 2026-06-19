from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import all_vehicles_keyboard, compact_vehicle_list_keyboard, records_dates_keyboard, status_keyboard, vehicle_card_keyboard, vehicle_status_text
from repositories.service_records import ServiceRecordRepository
from repositories.vehicles import VehicleRepository
from utils.plate import format_vehicle_number, normalize_plate, split_plate_and_region

router = Router()
class Search(StatesGroup): query = State()
class Comment(StatesGroup): text = State()

async def vehicle_text(vehicle, session: AsyncSession) -> str:
    count = await ServiceRecordRepository(session).count_for_vehicle(vehicle.id)
    return f"{format_vehicle_number(vehicle.plate_number, vehicle.region)}\nСтатус: {vehicle_status_text(vehicle.status)}\nКомментарий: {vehicle.note or '—'}\n\nВсего работ: {count}"

async def send_search_results(message, vehicles) -> None:
    if not vehicles:
        await message.answer("Ничего не найдено."); return
    await message.answer("Выберите ТС:", reply_markup=compact_vehicle_list_keyboard(vehicles))

@router.message(F.text == "Поиск автомобиля")
async def search_start(message: Message, state: FSMContext) -> None:
    await state.clear(); await state.set_state(Search.query)
    await message.answer("Введите номер или часть номера:")

@router.callback_query(F.data == "veh:search")
async def search_from_all(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear(); await state.set_state(Search.query)
    await call.message.answer("Введите номер или часть номера:"); await call.answer()

@router.message(Search.query)
async def search_run(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear(); q = message.text or ""
    plate, region = split_plate_and_region(q)
    normalized = f"{plate}{region}" if plate else normalize_plate(q)
    vehicles = await VehicleRepository(session).search(normalized)
    await send_search_results(message, vehicles)

@router.message(F.text == "Все автомобили")
async def all_vehicles(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    total = await VehicleRepository(session).count()
    await message.answer(f"Автомобилей в базе: {total}\nВыберите действие:", reply_markup=all_vehicles_keyboard())

@router.callback_query(F.data == "veh:problems")
async def problematic_vehicles(call: CallbackQuery, session: AsyncSession) -> None:
    vehicles = await VehicleRepository(session).problematic()
    await send_search_results(call.message, vehicles)
    await call.answer()

@router.callback_query(F.data.startswith("veh:open:"))
async def open_vehicle(call: CallbackQuery, session: AsyncSession) -> None:
    vehicle = await VehicleRepository(session).get(int(call.data.split(":")[-1]))
    if vehicle: await call.message.answer(await vehicle_text(vehicle, session), reply_markup=vehicle_card_keyboard(vehicle.id))
    await call.answer()

@router.callback_query(F.data.startswith("hist:list:"))
async def history_dates(call: CallbackQuery, session: AsyncSession) -> None:
    _, _, vid, off = call.data.split(":"); vehicle_id, offset = int(vid), int(off)
    records = await ServiceRecordRepository(session).history(vehicle_id, offset, 20)
    if not records: await call.message.answer("Работ по этому ТС пока нет."); await call.answer(); return
    await call.message.answer("Список работ по датам:", reply_markup=records_dates_keyboard(records, vehicle_id)); await call.answer()

@router.callback_query(F.data.startswith("hist:record:"))
async def history_record(call: CallbackQuery, session: AsyncSession) -> None:
    record = await ServiceRecordRepository(session).get(int(call.data.split(":")[-1]))
    if not record: await call.answer("Запись не найдена"); return
    items = ", ".join(i.name for i in record.items) or "без замен"
    performer = record.performer.first_name if record.performer else "—"
    await call.message.answer(f"{record.service_date:%d.%m.%Y %H:%M}\nТС: {format_vehicle_number(record.vehicle.plate_number, record.vehicle.region)}\nРаботы: {record.description}\nЗамены: {items}\nИсполнитель: {performer}")
    await call.answer()

@router.callback_query(F.data.startswith("veh:status:"))
async def status_start(call: CallbackQuery) -> None:
    vehicle_id = int(call.data.split(":")[-1])
    await call.message.answer("Выберите статус:", reply_markup=status_keyboard(vehicle_id)); await call.answer()

@router.callback_query(F.data.startswith("veh:set_status:"))
async def status_save(call: CallbackQuery, session: AsyncSession) -> None:
    _, _, _, vid, status = call.data.split(":")
    vehicle = await VehicleRepository(session).get(int(vid))
    if vehicle:
        vehicle.status = status
        await call.message.answer(f"Статус сохранён: {vehicle_status_text(status)}")
    await call.answer()

@router.callback_query(F.data.startswith("veh:note:"))
async def comment_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(vehicle_id=int(call.data.split(":")[-1])); await state.set_state(Comment.text)
    await call.message.answer("Введите комментарий по ТС:"); await call.answer()

@router.message(Comment.text)
async def comment_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data(); vehicle = await VehicleRepository(session).get(data["vehicle_id"])
    if vehicle: vehicle.note = message.text
    await state.clear(); await message.answer("Комментарий сохранён.")
