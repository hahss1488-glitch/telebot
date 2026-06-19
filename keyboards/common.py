from __future__ import annotations

from math import ceil
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить обслуживание"), KeyboardButton(text="🚗 Автомобили")],
    [KeyboardButton(text="📅 Отчёт за сегодня"), KeyboardButton(text="📊 Отчёт за месяц")],
    [KeyboardButton(text="🧰 Список задач")],
], resize_keyboard=True)

def vehicle_status_text(status: str) -> str:
    return "проблемные ТС 🔴" if status == "problem" else "нормальные ТС 🟢"

def all_vehicles_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Поиск по номеру", callback_data="veh:search")],
        [InlineKeyboardButton(text="Проблемные ТС 🔴", callback_data="veh:problems")],
    ])

def vehicle_card_keyboard(vehicle_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список работ", callback_data=f"hist:list:{vehicle_id}:0")],
        [InlineKeyboardButton(text="🚦 Изменить статус", callback_data=f"veh:status:{vehicle_id}"), InlineKeyboardButton(text="💬 Изменить комментарий", callback_data=f"veh:note:{vehicle_id}")],
        [InlineKeyboardButton(text="➕ Добавить обслуживание", callback_data=f"svc:add:{vehicle_id}")],
    ])

def status_keyboard(vehicle_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="нормальные ТС 🟢", callback_data=f"veh:set_status:{vehicle_id}:normal")],
        [InlineKeyboardButton(text="проблемные ТС 🔴", callback_data=f"veh:set_status:{vehicle_id}:problem")],
    ])

def service_items_keyboard(items, selected: set[int], columns: int = 3) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=(f"✅ {i.name}" if i.id in selected else i.name), callback_data=f"item:toggle:{i.id}") for i in items]
    rows = [buttons[i:i + columns] for i in range(0, len(buttons), columns)]
    rows.extend([
        [InlineKeyboardButton(text="✍️ Свой вариант", callback_data="item:custom"), InlineKeyboardButton(text="Без замен", callback_data="item:no_items")],
        [InlineKeyboardButton(text="🧹 Очистить", callback_data="item:clear"), InlineKeyboardButton(text="💾 Сохранить", callback_data="item:save")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def compact_vehicle_list_keyboard(vehicles) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🚗 {v.plate_number}{v.region}", callback_data=f"veh:open:{v.id}")] for v in vehicles
    ])

def region_missing_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить без региона", callback_data="svc:no_region")],
    ])

def records_dates_keyboard(records, vehicle_id: int) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=f"🛠 {r.service_date:%d.%m.%Y}", callback_data=f"hist:record:{r.id}")] for r in records]
    rows.append([InlineKeyboardButton(text="↩️ Назад к карточке", callback_data=f"veh:open:{vehicle_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def report_vehicles_keyboard(vehicles, scope: str, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    if scope == "today":
        visible = vehicles
    else:
        start = page * page_size
        visible = vehicles[start:start + page_size]
    rows = [[InlineKeyboardButton(text=f"🚗 {v.plate_number}{v.region}", callback_data=f"veh:open:{v.id}")] for v in visible]
    if scope == "month":
        pages = max(1, ceil(len(vehicles) / page_size))
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"report:month:{page - 1}"))
        if page + 1 < pages:
            nav.append(InlineKeyboardButton(text="➡️ Дальше", callback_data=f"report:month:{page + 1}"))
        if nav:
            rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)
