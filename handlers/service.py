from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.common import service_items_keyboard
from repositories.items import ReplacementItemRepository
from repositories.service_records import ServiceRecordRepository
from repositories.users import UserRepository
from repositories.vehicles import VehicleRepository
from services.vehicle_service import VehicleService

router = Router()

class AddService(StatesGroup):
    plate = State(); items = State(); custom = State()

@router.message(F.text == "Добавить обслуживание")
async def add_service_start(message: Message, state: FSMContext) -> None:
    await state.clear(); await state.set_state(AddService.plate)
    await message.answer("Введите номер и регион одной строкой.\nПример: ВТТ-360 RU797")

@router.message(AddService.plate)
async def add_service_plate(message: Message, state: FSMContext, session: AsyncSession) -> None:
    vehicle, created = await VehicleService(VehicleRepository(session)).get_or_create(message.text or "")
    items = await ReplacementItemRepository(session).list(active_only=True)
    await state.update_data(vehicle_id=vehicle.id, selected=[], custom_text=None)
    await state.set_state(AddService.items)
    status = "Создана карточка" if created else "Карточка найдена"
    await message.answer(f"{status}: {vehicle.plate_number} {vehicle.region}\nВыберите выполненные работы кнопками или нажмите «Свой вариант».", reply_markup=service_items_keyboard(items, set()))

@router.callback_query(F.data.startswith("svc:add:"))
async def add_service_from_card(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    items = await ReplacementItemRepository(session).list(active_only=True)
    await state.clear(); await state.update_data(vehicle_id=int(call.data.split(":")[-1]), selected=[], custom_text=None)
    await state.set_state(AddService.items)
    await call.message.answer("Выберите выполненные работы:", reply_markup=service_items_keyboard(items, set()))
    await call.answer()

@router.callback_query(AddService.items, F.data.startswith("item:toggle:"))
async def toggle_item(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    item_id = int(call.data.split(":")[-1]); data = await state.get_data(); selected = set(data.get("selected", []))
    selected.symmetric_difference_update({item_id}); await state.update_data(selected=list(selected))
    items = await ReplacementItemRepository(session).list(active_only=True)
    await call.message.edit_reply_markup(reply_markup=service_items_keyboard(items, selected)); await call.answer()

@router.callback_query(AddService.items, F.data == "item:clear")
async def clear_items(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(selected=[], custom_text=None)
    items = await ReplacementItemRepository(session).list(active_only=True)
    await call.message.edit_reply_markup(reply_markup=service_items_keyboard(items, set()))
    await call.answer("Выбор очищен")

@router.callback_query(AddService.items, F.data == "item:custom")
async def custom_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AddService.custom)
    await call.message.answer("Напишите свой вариант выполненных работ:")
    await call.answer()

@router.message(AddService.custom)
async def custom_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(custom_text=message.text or "")
    data = await state.get_data(); selected = set(data.get("selected", []))
    items = await ReplacementItemRepository(session).list(active_only=True)
    await state.set_state(AddService.items)
    await message.answer("Добавлено. Можно выбрать ещё работы или сохранить запись.", reply_markup=service_items_keyboard(items, selected))

@router.callback_query(AddService.items, F.data == "item:no_items")
async def no_items(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(selected=[], custom_text="Выполнены работы без замены элементов")
    await save_record(call, state, session)

@router.callback_query(AddService.items, F.data == "item:save")
async def save_record(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data(); selected_ids = set(data.get("selected", []))
    selected_items = [i for i in await ReplacementItemRepository(session).list(active_only=False) if i.id in selected_ids]
    parts = [i.name for i in selected_items]
    if data.get("custom_text"):
        parts.append(data["custom_text"])
    description = "; ".join(parts) or "Выполнены работы без замены элементов"
    user = await UserRepository(session).get_or_create(call.from_user) if call.from_user else None
    record = await ServiceRecordRepository(session).create(data["vehicle_id"], user.id if user else None, description, selected_ids)
    await state.clear()
    await call.message.answer(f"Запись #{record.id} сохранена: {description}")
    await call.answer()
