import telebot
from telebot import types
import logging
import os
import threading
import time
from datetime import datetime

# Импорт собственных модулей
from src.config import API_TOKEN, ADMIN_ID, MAX_PHOTOS, MAX_PHOTO_SIZE, PHOTO_LIFETIME_HOURS, SESSION_TIMEOUT_MINUTES
from src.data import PRICES, MATERIALS
from src.utils import (
    SpamProtection, check_session_timeout, update_activity,
    cleanup_user_files, cleanup_old_files, send_request_to_admin
)
from src.keyboards import (
    main_menu, cancel_menu, request_menu, photo_management_menu,
    material_types_inline, material_subtypes_inline, work_types_inline
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

# Инициализация бота
try:
    bot = telebot.TeleBot(API_TOKEN)
except Exception as e:
    logger.critical(f"Не удалось инициализировать бота: {str(e)}")
    exit()

# Инициализация защиты от спама
spam_protection = SpamProtection()

# Глобальное состояние пользователей
user_states = {}

# Создание необходимых папок
for folder in ['requests', 'logs']:
    os.makedirs(folder, exist_ok=True)

# --- Обработчики команд ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение"""
    user_id = message.from_user.id

    if spam_protection.is_spam(user_id):
        bot.send_message(message.chat.id, "⏳ Пожалуйста, подождите немного.")
        return

    # Очистка старой сессии при перезапуске
    if user_id in user_states:
        cleanup_user_files(user_id, user_states)

    user_states[user_id] = {"last_activity": datetime.now()}
    spam_protection.clear_user(user_id)

    welcome_text = (
        "👋 <b>Добро пожаловать в строительный помощник!</b>\n\n"
        "Я помогу вам:\n"
        "📊 Рассчитать предварительную смету на работы\n"
        "🧮 Посчитать необходимое количество материалов\n"
        "📩 Оставить заявку мастеру\n\n"
        "Выберите интересующий вас пункт меню ниже: 👇"
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О боте")
def about_bot(message):
    """Информация о боте"""
    if spam_protection.is_spam(message.from_user.id):
        return

    about_text = (
        "👷 <b>О строительном боте</b>\n\n"
        "Этот бот создан для упрощения взаимодействия между заказчиком и мастером-отделочником.\n\n"
        "<b>Возможности:</b>\n"
        "• <i>Актуальные цены</i> на основные виды отделочных работ.\n"
        "• <i>Умный калькулятор</i> плитки, кирпича и блоков с учетом запаса.\n"
        "• <i>Быстрая подача заявки</i> с возможностью прикрепить фотографии объекта.\n\n"
        "Всегда готов помочь в вашем ремонте! 🏠"
    )
    bot.send_message(
        message.chat.id,
        about_text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🔄 Сбросить")
def reset_state(message):
    """Сброс состояния пользователя"""
    user_id = message.from_user.id
    cleanup_user_files(user_id, user_states)
    user_states.pop(user_id, None)
    spam_protection.clear_user(user_id)

    bot.send_message(
        message.chat.id,
        "✅ Состояние успешно сброшено. Вы в главном меню.",
        reply_markup=main_menu()
    )

# --- Калькулятор материалов (Inline) ---

@bot.message_handler(func=lambda message: message.text == "🧮 Калькулятор материалов")
def material_calc_start(message):
    """Начало расчета материалов"""
    if spam_protection.is_spam(message.from_user.id):
        return

    user_states[message.from_user.id] = {
        "mode": "material_choice",
        "last_activity": datetime.now()
    }
    bot.send_message(
        message.chat.id,
        "🏗 <b>Выберите категорию материала:</b>",
        reply_markup=material_types_inline(),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('mat_'))
def handle_material_category(call):
    """Выбор категории материала через инлайн-кнопки"""
    user_id = call.from_user.id
    material_key = call.data.split('_')[1]

    user_states[user_id] = {
        "mode": "material_type",
        "material": material_key,
        "last_activity": datetime.now()
    }

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📐 <b>Выберите тип материала ({material_key}):</b>",
        reply_markup=material_subtypes_inline(material_key, MATERIALS),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_materials')
def back_to_materials(call):
    """Возврат к выбору категорий материалов"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🏗 <b>Выберите категорию материала:</b>",
        reply_markup=material_types_inline(),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('type_'))
def handle_material_subtype(call):
    """Выбор подтипа материала"""
    user_id = call.from_user.id
    subtype = call.data.split('_', 1)[1]

    state = user_states.get(user_id)
    if not state: return

    state["mode"] = "material_area_input"
    state["type"] = subtype
    state["last_activity"] = datetime.now()

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        f"📏 <b>Введите площадь в м² для {state['material']} ({subtype}):</b>\n"
        "Просто отправьте число в ответ на это сообщение.",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "material_area_input")
def process_material_area(message):
    """Обработка введенной площади для материалов"""
    user_id = message.from_user.id
    state = user_states[user_id]

    if message.text == "❌ Отмена":
        return send_welcome(message)

    try:
        area = float(message.text.replace(',', '.'))
        if area <= 0: raise ValueError

        params = MATERIALS[state["material"]][state["type"]]

        if state["material"] == "плитка":
            tiles_per_m2 = 1 / params["size"]
            total = area * tiles_per_m2 * (1 + params["waste"] / 100)
            result_text = f"🧩 Нужно примерно <b>{total:.0f} шт.</b> плитки."
        else:
            total = area * params["count"] * (1 + params["waste"] / 100)
            result_text = f"🧱 Нужно примерно <b>{total:.0f} шт.</b> материала."

        response = (
            f"✅ <b>Результат расчета:</b>\n\n"
            f"📦 Материал: {state['material']} ({state['type']})\n"
            f"📐 Площадь: {area} м²\n"
            f"📈 Запас: {params['waste']}%\n\n"
            f"<b>{result_text}</b>"
        )

        bot.send_message(message.chat.id, response, reply_markup=main_menu(), parse_mode="HTML")
        user_states.pop(user_id, None)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите положительное число (например: 15.5)")

# --- Расчет сметы ---

@bot.message_handler(func=lambda message: message.text == "📋 Рассчитать смету")
def estimate_start(message):
    """Начало расчета сметы"""
    if spam_protection.is_spam(message.from_user.id):
        return

    user_states[message.from_user.id] = {
        "mode": "estimate_work_selection",
        "last_activity": datetime.now()
    }

    bot.send_message(
        message.chat.id,
        "📝 <b>Выберите вид работ из списка или введите название:</b>\n"
        "(Например: <i>штукатурка</i> или <i>укладка плитки</i>)",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )

    # Также можно вывести инлайн-список популярных работ
    bot.send_message(
        message.chat.id,
        "Популярные работы:",
        reply_markup=work_types_inline(PRICES)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('work_'))
def handle_work_callback(call):
    """Выбор работы через инлайн-кнопку"""
    user_id = call.from_user.id
    if call.data == "work_manual":
        bot.answer_callback_query(call.id, "Введите название работы текстом")
        return

    work_name = call.data.split('_', 1)[1]

    user_states[user_id] = {
        "mode": "estimate_area_input",
        "work": work_name,
        "last_activity": datetime.now()
    }

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        f"📐 <b>Выбрано: {work_name}</b>\n"
        f"Введите объем работ (в {PRICES[work_name]['unit']}):",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "estimate_work_selection")
def process_work_text_input(message):
    """Поиск работы по текстовому вводу"""
    user_id = message.from_user.id
    work_input = message.text.lower().strip()

    if work_input == "❌ отмена":
        return send_welcome(message)

    # Поиск соответствия
    found_work = None
    if work_input in PRICES:
        found_work = work_input
    else:
        # Поиск по подстроке
        for w in PRICES:
            if work_input in w:
                found_work = w
                break

    if found_work:
        user_states[user_id] = {
            "mode": "estimate_area_input",
            "work": found_work,
            "last_activity": datetime.now()
        }
        bot.send_message(
            message.chat.id,
            f"✅ Найдено: <b>{found_work}</b>\n"
            f"Введите объем работ (в {PRICES[found_work]['unit']}):",
            reply_markup=cancel_menu(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "🔍 К сожалению, такая работа не найдена. Попробуйте ввести другое название или выберите из списка.",
            reply_markup=work_types_inline(PRICES)
        )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "estimate_area_input")
def process_estimate_area(message):
    """Расчет итоговой сметы"""
    user_id = message.from_user.id
    state = user_states[user_id]

    if message.text == "❌ Отмена":
        return send_welcome(message)

    try:
        area = float(message.text.replace(',', '.'))
        if area <= 0: raise ValueError

        work_data = PRICES[state["work"]]
        total_work = area * work_data["work_price"]

        response = (
            f"📊 <b>Предварительная смета:</b>\n\n"
            f"🔧 Работа: <i>{state['work'].capitalize()}</i>\n"
            f"📐 Объем: {area} {work_data['unit']}\n"
            f"💵 Цена за ед.: {work_data['work_price']} руб.\n"
            f"💰 <b>Итого за работу: {total_work:,.2f} руб.</b>"
        )

        if work_data["material"] != "-":
            mat_total = area * work_data["usage"]
            response += f"\n\n📦 <b>Материалы:</b>\nРекомендуется {work_data['material']}: ~{mat_total:.1f} {work_data['unit']}"

        bot.send_message(message.chat.id, response, reply_markup=main_menu(), parse_mode="HTML")
        user_states.pop(user_id, None)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число.")

# --- Оформление заявки ---

@bot.message_handler(func=lambda message: message.text == "📩 Оставить заявку")
def application_start(message):
    """Начало процесса оформления заявки"""
    if spam_protection.is_spam(message.from_user.id):
        return

    user_states[message.from_user.id] = {
        "mode": "app_contact",
        "app_data": {},
        "last_activity": datetime.now()
    }

    bot.send_message(
        message.chat.id,
        "📝 <b>Шаг 1/3: Контакты</b>\n\n"
        "Введите ваше имя и номер телефона для связи.\n"
        "Пример: <i>Алексей, +79001234567</i>",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_contact")
def process_app_contact(message):
    """Сохранение контактов и переход к описанию"""
    user_id = message.from_user.id
    contact_text = message.text.strip()

    if contact_text == "❌ Отмена":
        return send_welcome(message)

    if len(contact_text) < 5 or (',' not in contact_text and ' ' not in contact_text):
        bot.send_message(message.chat.id, "⚠️ Пожалуйста, введите имя и телефон (например: Иван, 8999...)")
        return

    user_states[user_id]["app_data"]["contact"] = contact_text
    user_states[user_id]["mode"] = "app_description"

    bot.send_message(
        message.chat.id,
        "📝 <b>Шаг 2/3: Описание задачи</b>\n\n"
        "Кратко опишите, что необходимо сделать (какие работы, объем, особенности):",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_description")
def process_app_description(message):
    """Сохранение описания и переход к срокам"""
    user_id = message.from_user.id

    if message.text == "❌ Отмена":
        return send_welcome(message)

    user_states[user_id]["app_data"]["description"] = message.text
    user_states[user_id]["mode"] = "app_deadline"

    bot.send_message(
        message.chat.id,
        "📝 <b>Шаг 3/3: Сроки</b>\n\n"
        "Укажите желаемые сроки начала или окончания работ:",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_deadline")
def process_app_deadline(message):
    """Сохранение сроков и переход к выбору фото"""
    user_id = message.from_user.id

    if message.text == "❌ Отмена":
        return send_welcome(message)

    state = user_states[user_id]
    state["app_data"]["deadline"] = message.text

    summary = (
        f"📋 <b>Ваша заявка:</b>\n\n"
        f"👤 <b>Контакты:</b> {state['app_data']['contact']}\n"
        f"🛠 <b>Работы:</b> {state['app_data']['description']}\n"
        f"📅 <b>Сроки:</b> {state['app_data']['deadline']}"
    )

    state["mode"] = "app_photo_choice"
    state["request_text"] = summary
    state["photos"] = []

    bot.send_message(message.chat.id, summary, parse_mode="HTML")
    bot.send_message(
        message.chat.id,
        "📸 Хотите добавить фотографии объекта для более точной оценки?",
        reply_markup=request_menu()
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_photo_choice")
def handle_app_photo_choice(message):
    """Выбор - отправлять с фото или без"""
    user_id = message.from_user.id

    if message.text == "📷 Прикрепить фото":
        user_states[user_id]["mode"] = "app_waiting_photos"
        bot.send_message(
            message.chat.id,
            f"Отправьте до {MAX_PHOTOS} фотографий. Когда закончите, нажмите кнопку «Отправить заявку».",
            reply_markup=photo_management_menu(0, MAX_PHOTOS)
        )
    elif message.text == "📤 Отправить без фото":
        finish_application(message)
    elif message.text == "🔙 Назад":
        application_start(message)

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_waiting_photos")
def handle_app_photo_upload(message):
    """Загрузка фотографий для заявки"""
    user_id = message.from_user.id
    state = user_states[user_id]

    if len(state["photos"]) >= MAX_PHOTOS:
        bot.reply_to(message, f"⚠️ Достигнут лимит в {MAX_PHOTOS} фото.")
        return

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        if file_info.file_size > MAX_PHOTO_SIZE:
            bot.reply_to(message, "❌ Файл слишком велик.")
            return

        downloaded_file = bot.download_file(file_info.file_path)
        filename = f"req_{user_id}_{int(time.time())}_{len(state['photos'])}.jpg"
        filepath = os.path.join('requests', filename)

        with open(filepath, 'wb') as f:
            f.write(downloaded_file)

        state["photos"].append(filepath)

        bot.reply_to(
            message,
            f"✅ Фото добавлено ({len(state['photos'])}/{MAX_PHOTOS})",
            reply_markup=photo_management_menu(len(state['photos']), MAX_PHOTOS)
        )
    except Exception as e:
        logger.error(f"Ошибка при загрузке фото: {e}")
        bot.reply_to(message, "❌ Ошибка при сохранении фото.")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_waiting_photos")
def handle_app_photo_management(message):
    """Управление списком фото или завершение заявки"""
    user_id = message.from_user.id

    if message.text == "📤 Отправить заявку":
        finish_application(message)
    elif message.text == "❌ Удалить последнее фото":
        if user_states[user_id]["photos"]:
            last_photo = user_states[user_id]["photos"].pop()
            if os.path.exists(last_photo):
                os.remove(last_photo)
            bot.send_message(
                message.chat.id,
                f"Удалено. Осталось фото: {len(user_states[user_id]['photos'])}",
                reply_markup=photo_management_menu(len(user_states[user_id]["photos"]), MAX_PHOTOS)
            )
    elif message.text == "🔙 Назад":
        application_start(message)

def finish_application(message):
    """Финальный этап отправки заявки"""
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state or "request_text" not in state:
        bot.send_message(message.chat.id, "❌ Ошибка сессии. Попробуйте создать заявку заново.", reply_markup=main_menu())
        return

    bot.send_message(message.chat.id, "⏳ Отправка заявки...", reply_markup=types.ReplyKeyboardRemove())

    success = send_request_to_admin(
        bot, ADMIN_ID, message.from_user,
        state["request_text"], state.get("photos")
    )

    # Очистка локальных файлов
    cleanup_user_files(user_id, user_states)

    if success:
        bot.send_message(
            message.chat.id,
            "✅ <b>Заявка успешно отправлена!</b>\n\n"
            "Мастер свяжется с вами в ближайшее время для уточнения деталей. Спасибо за доверие!",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ <b>Произошла ошибка при отправке.</b>\n\n"
            "Пожалуйста, свяжитесь с нами напрямую или попробуйте позже.",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )

    user_states.pop(user_id, None)

# --- Системные функции ---

@bot.message_handler(func=lambda message: True)
def handle_unexpected_messages(message):
    """Обработка всех прочих сообщений"""
    user_id = message.from_user.id

    # Проверка таймаута
    if check_session_timeout(user_id, user_states, SESSION_TIMEOUT_MINUTES):
        bot.send_message(message.chat.id, "⏰ Сессия истекла из-за длительного отсутствия активности.")
        return send_welcome(message)

    update_activity(user_id, user_states)

    if user_id in user_states and user_states[user_id].get("mode"):
        bot.send_message(
            message.chat.id,
            "❓ Я не совсем понял ваше сообщение. Пожалуйста, следуйте инструкциям или нажмите «🔄 Сбросить».",
            reply_markup=main_menu()
        )
    else:
        send_welcome(message)

def background_tasks():
    """Фоновые задачи: очистка старых файлов"""
    while True:
        cleanup_old_files('requests', PHOTO_LIFETIME_HOURS)
        time.sleep(3600)  # Раз в час

if __name__ == '__main__':
    # Запуск фонового потока
    threading.Thread(target=background_tasks, daemon=True).start()

    logger.info("Бот запущен")
    print("🚀 Бот запущен и готов к работе!")

    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        logger.error(f"Критическая ошибка polling: {e}")
        time.sleep(5)
