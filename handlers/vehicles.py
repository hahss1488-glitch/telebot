from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import vehicle_card_keyboard
from repositories.service_records import ServiceRecordRepository
from repositories.vehicles import VehicleRepository
from utils.plate import normalize_plate, normalize_region

router = Router()
class Search(StatesGroup): query = State()
class Note(StatesGroup): text = State()

async def vehicle_text(vehicle, session: AsyncSession) -> str:
    records = await ServiceRecordRepository(session).history(vehicle.id, 0, 3)
    count = await ServiceRecordRepository(session).count_for_vehicle(vehicle.id)
    last = records[0].service_date.strftime("%d.%m.%Y %H:%M") if records else "нет"
    works = "\n".join(f"• {r.description[:80]}" for r in records) or "нет"
    return f"🚗 {vehicle.plate_number} {vehicle.region}\nЗаметка: {vehicle.note or '—'}\nОбслуживаний: {count}\nПоследнее: {last}\nПоследние работы:\n{works}"

@router.message(F.text == "Поиск автомобиля")
async def search_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Search.query); await message.answer("Введите номер, часть номера, регион или текст заметки:")

@router.message(Search.query)
async def search_run(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear(); q = message.text or ""
    normalized = normalize_plate(q) or normalize_region(q) or q
    vehicles = await VehicleRepository(session).search(normalized)
    if not vehicles: await message.answer("Ничего не найдено."); return
    for vehicle in vehicles: await message.answer(await vehicle_text(vehicle, session), reply_markup=vehicle_card_keyboard(vehicle.id))

@router.message(F.text == "Все автомобили")
async def all_vehicles(message: Message, session: AsyncSession) -> None:
    vehicles = await VehicleRepository(session).all(limit=20)
    if not vehicles: await message.answer("Автомобилей пока нет."); return
    for vehicle in vehicles: await message.answer(await vehicle_text(vehicle, session), reply_markup=vehicle_card_keyboard(vehicle.id))

@router.callback_query(F.data.startswith("hist:"))
async def history(call: CallbackQuery, session: AsyncSession) -> None:
    _, vid, off = call.data.split(":"); vehicle_id, offset = int(vid), int(off)
    records = await ServiceRecordRepository(session).history(vehicle_id, offset, 5)
    if not records: await call.message.answer("История пуста."); await call.answer(); return
    lines = []
    for r in records:
        items = ", ".join(i.name for i in r.items) or "без замен"
        performer = r.performer.first_name if r.performer else "—"
        lines.append(f"{r.service_date:%d.%m.%Y %H:%M}\nРаботы: {r.description}\nЗамены: {items}\nИсполнитель: {performer}")
    await call.message.answer("\n\n".join(lines)); await call.answer()

@router.callback_query(F.data.startswith("veh:note:"))
async def note_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(vehicle_id=int(call.data.split(":")[-1])); await state.set_state(Note.text)
    await call.message.answer("Введите новую заметку:"); await call.answer()

@router.message(Note.text)
async def note_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data(); vehicle = await VehicleRepository(session).get(data["vehicle_id"])
    if vehicle: vehicle.note = message.text
    await state.clear(); await message.answer("Заметка сохранена.")

@router.callback_query(F.data.startswith("veh:del:"))
async def delete_vehicle(call: CallbackQuery, session: AsyncSession) -> None:
    vehicle = await VehicleRepository(session).get(int(call.data.split(":")[-1]))
    if vehicle: await VehicleRepository(session).delete(vehicle); await call.message.answer("Автомобиль удалён.")
    await call.answer()
