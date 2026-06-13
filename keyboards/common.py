from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Добавить обслуживание"), KeyboardButton(text="Поиск автомобиля")],
    [KeyboardButton(text="Все автомобили"), KeyboardButton(text="Отчёт за сегодня")],
    [KeyboardButton(text="Справочник замен"), KeyboardButton(text="Настройки")],
], resize_keyboard=True)

def vehicle_card_keyboard(vehicle_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить обслуживание", callback_data=f"svc:add:{vehicle_id}"), InlineKeyboardButton(text="История", callback_data=f"hist:{vehicle_id}:0")],
        [InlineKeyboardButton(text="Изменить заметку", callback_data=f"veh:note:{vehicle_id}"), InlineKeyboardButton(text="Редактировать автомобиль", callback_data=f"veh:edit:{vehicle_id}")],
        [InlineKeyboardButton(text="Удалить автомобиль", callback_data=f"veh:del:{vehicle_id}")],
    ])

def items_keyboard(items, selected: set[int]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=("✅ " if i.id in selected else "☐ ") + i.name, callback_data=f"item:toggle:{i.id}")] for i in items]
    rows.append([InlineKeyboardButton(text="Сохранить запись", callback_data="item:save")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
