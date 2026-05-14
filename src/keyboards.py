from telebot import types

def main_menu():
    """Главное меню бота"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📋 Рассчитать смету",
        "🧮 Калькулятор материалов",
        "📩 Оставить заявку",
        "🔄 Сбросить",
        "ℹ️ О боте"
    ]
    markup.add(*buttons)
    return markup

def cancel_menu():
    """Меню отмены действия"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Отмена")
    return markup

def request_menu():
    """Меню при оформлении заявки"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📷 Прикрепить фото", "📤 Отправить без фото", "🔙 Назад")
    return markup

def photo_management_menu(photo_count, max_photos):
    """Меню управления фотографиями в заявке"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📤 Отправить заявку"]
    if photo_count > 0:
        buttons.append("❌ Удалить последнее фото")
    buttons.append("🔙 Назад")
    markup.add(*buttons)
    return markup

def material_types_inline():
    """Инлайн-меню выбора категории материалов"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🧱 Плитка", callback_data="mat_плитка"),
        types.InlineKeyboardButton("🧱 Кирпич", callback_data="mat_кирпич"),
        types.InlineKeyboardButton("🧱 Газоблок", callback_data="mat_газоблок")
    )
    return markup

def material_subtypes_inline(material_key, materials_dict):
    """Инлайн-меню выбора подтипа материала"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    if material_key in materials_dict:
        for subtype in materials_dict[material_key].keys():
            markup.add(types.InlineKeyboardButton(subtype, callback_data=f"type_{subtype}"))
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_materials"))
    return markup

def work_types_inline(prices_dict):
    """Инлайн-меню выбора вида работ (постранично или сокращенно)"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Показываем основные категории или первые 10 для примера
    for work in list(prices_dict.keys())[:10]:
        markup.add(types.InlineKeyboardButton(work.capitalize(), callback_data=f"work_{work}"))
    markup.add(types.InlineKeyboardButton("🔍 Другие работы (введите текстом)", callback_data="work_manual"))
    return markup
