import os
import time
from datetime import datetime
from telebot import types

from core.config import API_TOKEN, ADMIN_ID, MAX_PHOTOS, MAX_PHOTO_SIZE, SESSION_TIMEOUT_MINUTES, REQUESTS_DIR
from utils.helpers import SpamProtection, cleanup_files
from services.estimate_service import calculate_estimate, find_similar_works
from services.material_service import calculate_material_needs
from services.application_service import format_application_for_admin, send_application
from bot.keyboards import (
    main_menu, cancel_menu, material_categories_inline, material_subtypes_inline,
    work_types_inline, photo_management_menu, request_photo_choice_menu
)

spam_protection = SpamProtection()
user_states = {}

def register_handlers(bot):

    def check_timeout(user_id):
        if user_id in user_states:
            last = user_states[user_id].get('last_activity')
            if last and datetime.now() - last > datetime.timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                cleanup_files(user_states[user_id].get('photos', []))
                user_states.pop(user_id, None)
                return True
        return False

    def update_act(user_id):
        if user_id in user_states:
            user_states[user_id]['last_activity'] = datetime.now()

    @bot.message_handler(commands=['start', 'help'])
    def welcome(message):
        user_id = message.from_user.id
        if spam_protection.is_spam(user_id): return

        user_states[user_id] = {'last_activity': datetime.now()}
        bot.send_message(
            message.chat.id,
            "👋 <b>Добро пожаловать!</b>\nЯ помогу вам с расчетами и заявками на ремонт.",
            reply_markup=main_menu(), parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: m.text == "ℹ️ О боте")
    def about(message):
        bot.send_message(message.chat.id, "🤖 Бот-помощник для отделочных работ.\nВерсия: 2.0 (Modular)")

    @bot.message_handler(func=lambda m: m.text == "🔄 Сбросить")
    def reset(message):
        uid = message.from_user.id
        if uid in user_states:
            cleanup_files(user_states[uid].get('photos', []))
            user_states.pop(uid, None)
        bot.send_message(message.chat.id, "✅ Состояние сброшено", reply_markup=main_menu())

    # --- Estimate Flow ---
    @bot.message_handler(func=lambda m: m.text == "📋 Рассчитать смету")
    def est_start(message):
        user_states[message.from_user.id] = {"mode": "est_work", "last_activity": datetime.now()}
        bot.send_message(message.chat.id, "Выберите вид работ или введите название:", reply_markup=work_types_inline())

    @bot.callback_query_handler(func=lambda c: c.data.startswith('work_'))
    def est_work_callback(call):
        if call.data == "work_manual": return
        work = call.data.split('_', 1)[1]
        user_states[call.from_user.id].update({"mode": "est_area", "work": work})
        bot.send_message(call.message.chat.id, f"Введите объем работ для '<b>{work}</b>':", parse_mode="HTML", reply_markup=cancel_menu())

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "est_work")
    def est_work_text(message):
        if message.text == "❌ Отмена": return welcome(message)
        similar = find_similar_works(message.text)
        if similar:
            user_states[message.from_user.id].update({"mode": "est_area", "work": similar[0]})
            bot.send_message(message.chat.id, f"Найдено: <b>{similar[0]}</b>. Введите объем:", parse_mode="HTML", reply_markup=cancel_menu())
        else:
            bot.send_message(message.chat.id, "Ничего не найдено. Попробуйте еще раз.")

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "est_area")
    def est_area_proc(message):
        if message.text == "❌ Отмена": return welcome(message)
        try:
            area = float(message.text.replace(',', '.'))
            res = calculate_estimate(user_states[message.from_user.id]['work'], area)
            text = f"📊 <b>Смета:</b>\nРабота: {res['work_name']}\nИтого: <b>{res['total_price']:,.2f} руб.</b>"
            if res['material_info']:
                text += f"\n\n📦 Материалы: {res['material_info']['name']} (~{res['material_info']['amount']:.1f})"
            bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu())
            user_states.pop(message.from_user.id)
        except ValueError:
            bot.send_message(message.chat.id, "Введите число!")

    # --- Material Flow ---
    @bot.message_handler(func=lambda m: m.text == "🧮 Калькулятор материалов")
    def mat_start(message):
        user_states[message.from_user.id] = {"mode": "mat_cat", "last_activity": datetime.now()}
        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=material_categories_inline())

    @bot.callback_query_handler(func=lambda c: c.data.startswith('mat_'))
    def mat_cat_callback(call):
        cat = call.data.split('_')[1]
        user_states[call.from_user.id].update({"mode": "mat_type", "category": cat})
        bot.edit_message_text("Выберите тип:", call.message.chat.id, call.message.message_id, reply_markup=material_subtypes_inline(cat))

    @bot.callback_query_handler(func=lambda c: c.data.startswith('type_'))
    def mat_type_callback(call):
        t = call.data.split('_')[1]
        user_states[call.from_user.id].update({"mode": "mat_area", "type": t})
        bot.send_message(call.message.chat.id, f"Введите площадь для {t}:", reply_markup=cancel_menu())

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "mat_area")
    def mat_area_proc(message):
        if message.text == "❌ Отмена": return welcome(message)
        try:
            area = float(message.text.replace(',', '.'))
            state = user_states[message.from_user.id]
            res = calculate_material_needs(state['category'], state['type'], area)
            text = f"🧮 <b>Расчет:</b>\n{res['subtype']}\nНужно: <b>{res['total_count']:.0f} шт.</b>"
            bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu())
            user_states.pop(message.from_user.id)
        except:
            bot.send_message(message.chat.id, "Ошибка ввода.")

    # --- Application Flow ---
    @bot.message_handler(func=lambda m: m.text == "📩 Оставить заявку")
    def app_start(message):
        user_states[message.from_user.id] = {"mode": "app_contact", "app_data": {}, "last_activity": datetime.now()}
        bot.send_message(message.chat.id, "Шаг 1/3: Введите имя и телефон:", reply_markup=cancel_menu())

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_contact")
    def app_contact(message):
        if message.text == "❌ Отмена": return welcome(message)
        user_states[message.from_user.id]['app_data']['contact'] = message.text
        user_states[message.from_user.id]['mode'] = "app_desc"
        bot.send_message(message.chat.id, "Шаг 2/3: Опишите задачу:")

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_desc")
    def app_desc(message):
        if message.text == "❌ Отмена": return welcome(message)
        user_states[message.from_user.id]['app_data']['description'] = message.text
        user_states[message.from_user.id]['mode'] = "app_deadline"
        bot.send_message(message.chat.id, "Шаг 3/3: Сроки:")

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_deadline")
    def app_deadline(message):
        if message.text == "❌ Отмена": return welcome(message)
        state = user_states[message.from_user.id]
        state['app_data']['deadline'] = message.text
        state['mode'] = "app_photo_choice"
        state['photos'] = []
        bot.send_message(message.chat.id, "Желаете добавить фото?", reply_markup=request_photo_choice_menu())

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_photo_choice")
    def app_photo_choice(message):
        if message.text == "📷 Прикрепить фото":
            user_states[message.from_user.id]['mode'] = "app_photos"
            bot.send_message(message.chat.id, "Отправляйте фото, затем нажмите 'Отправить заявку'", reply_markup=photo_management_menu(0, MAX_PHOTOS))
        elif message.text == "📤 Отправить без фото":
            finish_app(message)
        else: return welcome(message)

    @bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_photos")
    def app_photo_upload(message):
        state = user_states[message.from_user.id]
        if len(state['photos']) >= MAX_PHOTOS: return
        file_info = bot.get_file(message.photo[-1].file_id)
        down = bot.download_file(file_info.file_path)
        path = os.path.join(REQUESTS_DIR, f"{message.from_user.id}_{int(time.time())}.jpg")
        with open(path, 'wb') as f: f.write(down)
        state['photos'].append(path)
        bot.reply_to(message, f"Добавлено {len(state['photos'])}/{MAX_PHOTOS}", reply_markup=photo_management_menu(len(state['photos']), MAX_PHOTOS))

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "app_photos")
    def app_photo_mgmt(message):
        if message.text == "📤 Отправить заявку": finish_app(message)
        elif message.text == "❌ Удалить последнее фото":
            if user_states[message.from_user.id]['photos']:
                p = user_states[message.from_user.id]['photos'].pop()
                if os.path.exists(p): os.remove(p)
                bot.send_message(message.chat.id, "Удалено", reply_markup=photo_management_menu(len(user_states[message.from_user.id]['photos']), MAX_PHOTOS))
        else: return welcome(message)

    def finish_app(message):
        state = user_states[message.from_user.id]
        text = format_application_for_admin(message.from_user.__dict__, state['app_data'])
        if send_application(bot, ADMIN_ID, text, state.get('photos')):
            bot.send_message(message.chat.id, "✅ Заявка отправлена!", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "❌ Ошибка отправки.")
        cleanup_files(state.get('photos', []))
        user_states.pop(message.from_user.id)

    @bot.message_handler(func=lambda m: True)
    def catch_all(message):
        uid = message.from_user.id
        if check_timeout(uid):
            bot.send_message(message.chat.id, "⏰ Сессия истекла. Начните заново.")
            return welcome(message)

        update_act(uid)
        welcome(message)
