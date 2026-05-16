from telebot import types
from data.prices import PRICES
from data.materials import MATERIALS

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📋 Рассчитать смету", "🧮 Калькулятор материалов", "📩 Оставить заявку", "🔄 Сбросить", "ℹ️ О боте")
    return markup

def cancel_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Отмена")
    return markup

def material_categories_inline():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(cat.capitalize(), callback_data=f"mat_{cat}") for cat in MATERIALS.keys()]
    markup.add(*buttons)
    return markup

def material_subtypes_inline(category: str):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if category in MATERIALS:
        for subtype in MATERIALS[category].keys():
            markup.add(types.InlineKeyboardButton(subtype, callback_data=f"type_{subtype}"))
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_materials"))
    return markup

def work_types_inline():
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Popular/First 10
    for work in list(PRICES.keys())[:10]:
        markup.add(types.InlineKeyboardButton(work.capitalize(), callback_data=f"work_{work}"))
    markup.add(types.InlineKeyboardButton("🔍 Другие (введите текст)", callback_data="work_manual"))
    return markup

def photo_management_menu(photo_count: int, max_photos: int):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📤 Отправить заявку"]
    if photo_count > 0:
        buttons.append("❌ Удалить последнее фото")
    buttons.append("🔙 Назад")
    markup.add(*buttons)
    return markup

def request_photo_choice_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📷 Прикрепить фото", "📤 Отправить без фото", "🔙 Назад")
    return markup
