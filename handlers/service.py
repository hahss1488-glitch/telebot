from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import items_keyboard, vehicle_card_keyboard
from repositories.items import ReplacementItemRepository
from repositories.service_records import ServiceRecordRepository
from repositories.users import UserRepository
from repositories.vehicles import VehicleRepository
from services.vehicle_service import VehicleService

router = Router()

class AddService(StatesGroup):
    plate = State(); region = State(); description = State(); items = State()

@router.message(F.text == "Добавить обслуживание")
async def add_service_start(message: Message, state: FSMContext) -> None:
    await state.clear(); await state.set_state(AddService.plate)
    await message.answer("Введите номер автомобиля:")

@router.message(AddService.plate)
async def add_service_plate(message: Message, state: FSMContext) -> None:
    await state.update_data(plate=message.text or ""); await state.set_state(AddService.region)
    await message.answer("Введите регион:")

@router.message(AddService.region)
async def add_service_region(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    vehicle, created = await VehicleService(VehicleRepository(session)).get_or_create(data["plate"], message.text or "")
    await state.update_data(vehicle_id=vehicle.id, selected=[]); await state.set_state(AddService.description)
    await message.answer(("Создана карточка. " if created else "Карточка найдена. ") + "Введите описание работ:")

@router.callback_query(F.data.startswith("svc:add:"))
async def add_service_from_card(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear(); await state.update_data(vehicle_id=int(call.data.split(":")[-1]), selected=[]); await state.set_state(AddService.description)
    await call.message.answer("Введите описание работ:"); await call.answer()

@router.message(AddService.description)
async def add_service_description(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(description=message.text or "")
    items = await ReplacementItemRepository(session).list(active_only=True)
    await state.set_state(AddService.items)
    await message.answer("Выберите заменённые элементы:", reply_markup=items_keyboard(items, set()))

@router.callback_query(AddService.items, F.data.startswith("item:toggle:"))
async def toggle_item(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    item_id = int(call.data.split(":")[-1]); data = await state.get_data(); selected = set(data.get("selected", []))
    selected.symmetric_difference_update({item_id}); await state.update_data(selected=list(selected))
    items = await ReplacementItemRepository(session).list(active_only=True)
    await call.message.edit_reply_markup(reply_markup=items_keyboard(items, selected)); await call.answer()

@router.callback_query(AddService.items, F.data == "item:save")
async def save_record(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    user = await UserRepository(session).get_or_create(call.from_user) if call.from_user else None
    record = await ServiceRecordRepository(session).create(data["vehicle_id"], user.id if user else None, data["description"], set(data.get("selected", [])))
    await state.clear()
    await call.message.answer(f"Запись обслуживания #{record.id} сохранена.")
    await call.answer()
