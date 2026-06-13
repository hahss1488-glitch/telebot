from __future__ import annotations
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.items import ReplacementItemRepository

router = Router()
class ItemAdd(StatesGroup): name = State(); description = State()

def dict_keyboard(items) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"{i.sort_order}. {'✅' if i.is_active else '🚫'} {i.name}", callback_data=f"dict:item:{i.id}")] for i in items]
    rows.append([InlineKeyboardButton(text="Добавить элемент", callback_data="dict:add")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

@router.message(F.text == "Справочник замен")
async def dictionary(message: Message, session: AsyncSession) -> None:
    await message.answer("Справочник заменяемых элементов:", reply_markup=dict_keyboard(await ReplacementItemRepository(session).list()))

@router.callback_query(F.data == "dict:add")
async def add_item_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ItemAdd.name); await call.message.answer("Название элемента:"); await call.answer()

@router.message(ItemAdd.name)
async def add_item_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text or ""); await state.set_state(ItemAdd.description); await message.answer("Описание элемента:")

@router.message(ItemAdd.description)
async def add_item_desc(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data(); await ReplacementItemRepository(session).create(data["name"], message.text)
    await state.clear(); await message.answer("Элемент добавлен.")

@router.callback_query(F.data.startswith("dict:item:"))
async def item_actions(call: CallbackQuery, session: AsyncSession) -> None:
    item = await ReplacementItemRepository(session).get(int(call.data.split(":")[-1]))
    if not item: await call.answer("Не найдено"); return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вкл/выкл", callback_data=f"dict:toggle:{item.id}"), InlineKeyboardButton(text="Удалить", callback_data=f"dict:delete:{item.id}")],
    ])
    await call.message.answer(f"{item.name}\n{item.description or ''}\nПорядок: {item.sort_order}", reply_markup=kb); await call.answer()

@router.callback_query(F.data.startswith("dict:toggle:"))
async def toggle_item(call: CallbackQuery, session: AsyncSession) -> None:
    item = await ReplacementItemRepository(session).get(int(call.data.split(":")[-1]))
    if item: item.is_active = not item.is_active; await call.message.answer("Статус изменён.")
    await call.answer()

@router.callback_query(F.data.startswith("dict:delete:"))
async def delete_item(call: CallbackQuery, session: AsyncSession) -> None:
    item = await ReplacementItemRepository(session).get(int(call.data.split(":")[-1]))
    if item: await session.delete(item); await call.message.answer("Элемент удалён.")
    await call.answer()
