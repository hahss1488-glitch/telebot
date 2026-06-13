from __future__ import annotations

from math import ceil
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Добавить обслуживание"), KeyboardButton(text="Поиск автомобиля")],
    [KeyboardButton(text="Все автомобили"), KeyboardButton(text="Отчёт за сегодня")],
    [KeyboardButton(text="Справочник замен")],
], resize_keyboard=True)

def vehicle_card_keyboard(vehicle_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить обслуживание", callback_data=f"svc:add:{vehicle_id}"), InlineKeyboardButton(text="История", callback_data=f"hist:{vehicle_id}:0")],
        [InlineKeyboardButton(text="Изменить заметку", callback_data=f"veh:note:{vehicle_id}"), InlineKeyboardButton(text="Удалить автомобиль", callback_data=f"veh:del:{vehicle_id}")],
    ])

def service_items_keyboard(items, selected: set[int], columns: int = 3) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=(f"[{i.name}]" if i.id in selected else i.name), callback_data=f"item:toggle:{i.id}") for i in items]
    rows = [buttons[i:i + columns] for i in range(0, len(buttons), columns)]
    rows.extend([
        [InlineKeyboardButton(text="Свой вариант", callback_data="item:custom"), InlineKeyboardButton(text="Без замен", callback_data="item:no_items")],
        [InlineKeyboardButton(text="Очистить выбор", callback_data="item:clear"), InlineKeyboardButton(text="Сохранить", callback_data="item:save")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def compact_vehicle_list_keyboard(vehicles, page: int, page_size: int, total: int) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"{v.plate_number} {v.region}", callback_data=f"veh:open:{v.id}")] for v in vehicles]
    pages = max(1, ceil(total / page_size))
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="Назад", callback_data=f"veh:list:{page - 1}"))
    if page + 1 < pages:
        nav.append(InlineKeyboardButton(text="Дальше", callback_data=f"veh:list:{page + 1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)
