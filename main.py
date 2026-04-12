import telebot
from telebot import types
from datetime import datetime, timedelta
import os
import logging
from config import API_TOKEN, USER_ID
import time
import threading
from collections import defaultdict

# Настройка логгирования
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


# Защита от спама
class SpamProtection:
    def __init__(self, max_messages=5, time_window=60):
        self.user_messages = defaultdict(list)
        self.max_messages = max_messages
        self.time_window = time_window

    def is_spam(self, user_id):
        now = time.time()
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < self.time_window
        ]

        if len(self.user_messages[user_id]) >= self.max_messages:
            return True

        self.user_messages[user_id].append(now)
        return False

    def clear_user(self, user_id):
        self.user_messages.pop(user_id, None)


spam_protection = SpamProtection()

# Проверка конфигурации
if API_TOKEN == 'your_token_here' or not USER_ID:
    logger.error("Конфигурация не настроена!")
    print("❌ Ошибка! Проверьте config.py:")
    print(f"Токен: {'установлен' if API_TOKEN != 'your_token_here' else 'НЕ настроен'}")
    print(f"ID админа: {USER_ID if USER_ID else 'НЕ указан'}")
    exit()

# Создаем папки если их нет
for folder in ['requests', 'logs']:
    os.makedirs(folder, exist_ok=True)

# Константы
MAX_PHOTOS = 3
MAX_PHOTO_SIZE = 15 * 1024 * 1024
PHOTO_LIFETIME_HOURS = 24
SESSION_TIMEOUT = timedelta(minutes=30)

# Словарь с ценами (оставляем без изменений)
PRICES = {
    # Ремонтные работы
    "косметический ремонт квартиры": {"work_price": 5000, "unit": "м²", "material": "комплекс", "usage": 1},
    "капитальный ремонт квартиры": {"work_price": 15000, "unit": "м²", "material": "комплекс", "usage": 1},
    "дизайнерский ремонт квартир": {"work_price": 30000, "unit": "м²", "material": "комплекс", "usage": 1},
    "капитальный ремонт дома": {"work_price": 15000, "unit": "м²", "material": "комплекс", "usage": 1},
    "косметический ремонт дома": {"work_price": 5000, "unit": "м²", "material": "комплекс", "usage": 1},

    # Подготовительные работы
    "шпатлевание": {"work_price": 250, "unit": "м²", "material": "шпаклевка", "usage": 1.5},
    "штукатурка": {"work_price": 500, "unit": "м²", "material": "гипс", "usage": 10},
    "грунтовка": {"work_price": 100, "unit": "м²", "material": "грунт", "usage": 0.1},
    "шлифовка": {"work_price": 100, "unit": "м²", "material": "сетка", "usage": 0.3},
    "демонтаж обоев": {"work_price": 100, "unit": "м²", "material": "-", "usage": 0},

    # Остальные цены...
    "покраска валиком один слой": {"work_price": 200, "unit": "м²", "material": "краска", "usage": 0.15},
    "обои флизелин винил без рисунка": {"work_price": 200, "unit": "м²", "material": "клей", "usage": 0.3},
    "обои флизелин винил с рисунком": {"work_price": 250, "unit": "м²", "material": "клей", "usage": 0.4},
    "бумажные обои": {"work_price": 500, "unit": "м²", "material": "клей", "usage": 0.2},
    "текстильные обои": {"work_price": 1000, "unit": "м²", "material": "клей", "usage": 0.5},
    "стеклообои": {"work_price": 1000, "unit": "м²", "material": "клей", "usage": 0.6},
    "жидкие обои": {"work_price": 500, "unit": "м²", "material": "смесь", "usage": 1.2},
    "колеровка краски": {"work_price": 100, "unit": "м²", "material": "колер", "usage": 0.05},
    "кладка газобетонных блоков": {"work_price": 600, "unit": "м²", "material": "клей", "usage": 5},
    "кладка кирпича": {"work_price": 400, "unit": "м²", "material": "раствор", "usage": 7},
    "кладка пеноблока": {"work_price": 450, "unit": "м²", "material": "клей", "usage": 4.5},
    "облицовка гипсокартоном": {"work_price": 1000, "unit": "м²", "material": "профиль+ГКЛ", "usage": 1.1},
    "работа с серпянкой": {"work_price": 60, "unit": "м.п.", "material": "лента", "usage": 1},
    "укладка плитки": {"work_price": 1000, "unit": "м²", "material": "клей", "usage": 4},
    "чистый шов плитка": {"work_price": 1000, "unit": "м.п.", "material": "затирка", "usage": 0.1},
    "вырезы в плитке": {"work_price": 1500, "unit": "шт", "material": "-", "usage": 0},
    "укладка плитки по рисунку": {"work_price": 7000, "unit": "м²", "material": "клей", "usage": 5},
    "зарезка плитки на 45°": {"work_price": 1500, "unit": "м.п.", "material": "-", "usage": 0},
    "установка смесителя": {"work_price": 500, "unit": "шт", "material": "уплотнитель", "usage": 1},
    "прокладка труб водоснабжения": {"work_price": 500, "unit": "м.п.", "material": "трубы", "usage": 1},
    "штробление под сантехнику": {"work_price": 700, "unit": "м.п.", "material": "-", "usage": 0},
    "установка акриловой ванны": {"work_price": 3000, "unit": "шт", "material": "пеня", "usage": 1},
    "установка розетки": {"work_price": 400, "unit": "шт", "material": "-", "usage": 0},
    "установка выключателя": {"work_price": 600, "unit": "шт", "material": "-", "usage": 0},
    "разводка электрики": {"work_price": 500, "unit": "м²", "material": "кабель", "usage": 3},
    "штробление под электропроводку": {"work_price": 600, "unit": "м.п.", "material": "-", "usage": 0},
    "установка маяков": {"work_price": 120, "unit": "м.п.", "material": "маяки", "usage": 1},
    "услуги грузчика": {"work_price": 1000, "unit": "час", "material": "-", "usage": 0},
    "уборка": {"work_price": 4000, "unit": "объект", "material": "-", "usage": 0},
    "удаление грибков": {"work_price": 3000, "unit": "м²", "material": "химия", "usage": 0.5}
}

# Словарь для калькулятора материалов
MATERIALS = {
    "плитка": {
        "20x30 см": {"size": 0.06, "waste": 10},
        "30x30 см": {"size": 0.09, "waste": 10},
        "40x40 см": {"size": 0.16, "waste": 10}
    },
    "кирпич": {
        "одинарный": {"count": 51, "waste": 5},
        "полуторный": {"count": 39, "waste": 5},
        "двойной": {"count": 26, "waste": 5}
    },
    "газоблок": {
        "600x200x300": {"count": 6.67, "waste": 5},
        "600x250x300": {"count": 5.56, "waste": 5},
        "600x200x400": {"count": 5.00, "waste": 5}
    }
}

# Состояния пользователей с таймаутом
user_states = {}


def check_session_timeout(user_id):
    """Проверка таймаута сессии"""
    if user_id in user_states:
        last_activity = user_states[user_id].get('last_activity')
        if last_activity and datetime.now() - last_activity > SESSION_TIMEOUT:
            cleanup_user_files(user_id)
            user_states.pop(user_id, None)
            return True
    return False


def update_activity(user_id):
    """Обновление времени последней активности"""
    if user_id in user_states:
        user_states[user_id]['last_activity'] = datetime.now()


def cleanup_user_files(user_id):
    """Очистка файлов пользователя"""
    if user_id in user_states and 'photos' in user_states[user_id]:
        for photo_path in user_states[user_id]['photos']:
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except:
                pass


def main_menu():
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Отмена")
    return markup


def request_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📷 Прикрепить фото", "📤 Отправить без фото", "🔙 Назад")
    return markup


def cleanup_old_files():
    """Очистка старых файлов"""
    try:
        now = datetime.now()
        for filename in os.listdir('requests'):
            file_path = os.path.join('requests', filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_time).total_seconds() > PHOTO_LIFETIME_HOURS * 3600:
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Ошибка при очистке файлов: {str(e)}")


def send_request_to_admin(user, request_text, photos=None):
    """Отправка заявки админу"""
    try:
        user_info = (
            f"👤 Клиент:\n"
            f"• Имя: {user.first_name}\n"
            f"• Фамилия: {user.last_name or 'не указана'}\n"
            f"• Username: @{user.username or 'нет'}\n"
            f"• ID: {user.id}"
        )

        full_text = f"📩 Новая заявка\n\n{request_text}\n\n{user_info}"

        if photos:
            # Отправка первого фото с описанием
            with open(photos[0], 'rb') as photo:
                bot.send_photo(USER_ID, photo, caption=full_text, parse_mode="HTML")

            # Отправка остальных фото
            for photo_path in photos[1:]:
                try:
                    with open(photo_path, 'rb') as photo:
                        bot.send_photo(USER_ID, photo)
                except Exception as e:
                    logger.error(f"Ошибка отправки дополнительного фото: {str(e)}")
        else:
            bot.send_message(USER_ID, full_text, parse_mode="HTML")

        return True

    except Exception as e:
        logger.error(f"Ошибка при отправке заявки админу: {str(e)}")
        return False


@bot.message_handler(commands=['start', 'help'])
def start(message):
    user_id = message.from_user.id

    # Проверка спама
    if spam_protection.is_spam(user_id):
        bot.send_message(message.chat.id, "⏳ Подождите немного перед следующим запросом")
        return

    # Очистка старой сессии
    if user_id in user_states:
        cleanup_user_files(user_id)

    user_states[user_id] = {"last_activity": datetime.now()}
    spam_protection.clear_user(user_id)

    bot.send_message(
        message.chat.id,
        "👷 Строительный бот-помощник\nВыберите действие:",
        reply_markup=main_menu()
    )
    logger.info(f"Пользователь {user_id} начал работу с ботом")


@bot.message_handler(func=lambda message: message.text == "ℹ️ О боте")
def about(message):
    if spam_protection.is_spam(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "🤖 <b>Строительный бот-помощник</b>\n\n"
        "Этот бот поможет вам:\n"
        "• Рассчитать стоимость работ\n"
        "• Посчитать необходимое количество материалов\n"
        "• Оставить заявку на выполнение работ\n\n"
        "Для начала работы выберите нужный пункт в меню.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🔄 Сбросить")
def reset(message):
    user_id = message.from_user.id
    # Очистка файлов и состояния
    cleanup_user_files(user_id)
    user_states.pop(user_id, None)
    spam_protection.clear_user(user_id)
    bot.send_message(message.chat.id, "✅ Состояние сброшено", reply_markup=main_menu())
    logger.info(f"Пользователь {user_id} сбросил состояние")


@bot.message_handler(func=lambda message: message.text == "📋 Рассчитать смету")
def estimate(message):
    if spam_protection.is_spam(message.from_user.id):
        return

    if check_session_timeout(message.from_user.id):
        bot.send_message(message.chat.id, "⏰ Сессия истекла. Начните заново.")
        return start(message)

    works_list = "\n".join([f"▪️ {work}" for work in list(PRICES.keys())[:20]])  # Показываем первые 20
    works_list += "\n▪️ ... и другие"

    user_states[message.from_user.id] = {
        "mode": "estimate",
        "last_activity": datetime.now()
    }

    bot.send_message(
        message.chat.id,
        f"🔹 <b>Доступные виды работ:</b>\n{works_list}\n\n"
        "📝 <b>Введите запрос в формате:</b>\n"
        "<code>площадь, вид работы</code>\n"
        "Пример: <code>15, штукатурка</code>",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "estimate")
def process_estimate(message):
    user_id = message.from_user.id

    if message.text == "❌ Отмена":
        user_states.pop(user_id, None)
        return start(message)

    if spam_protection.is_spam(user_id):
        return

    try:
        area, work = map(str.strip, message.text.split(',', 1))
        area = float(area)
        work = work.lower()

        if work not in PRICES:
            similar = [w for w in PRICES if work in w][:3]
            reply = "❌ Вид работ не найден. Возможно:\n" + "\n".join(similar) if similar else "❌ Вид работ не найден"
            bot.send_message(message.chat.id, reply, reply_markup=main_menu())
            logger.warning(f"Пользователь {user_id} ввел неизвестный вид работы: {work}")
            return

        price = PRICES[work]
        total = area * price["work_price"]

        response = (
            f"📊 <b>Смета:</b> {work.capitalize()}\n"
            f"▫️ Площадь: {area} {price['unit']}\n"
            f"▫️ Цена: {price['work_price']} руб/{price['unit']}\n"
            f"▫️ <b>Итого: {total:.2f} руб</b>"
        )

        if price["material"] != "-":
            response += f"\n\n📦 Материалы: {price['material']}\nНужно: {area * price['usage']:.1f} {price['unit']}"

        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, response, reply_markup=main_menu(), parse_mode="HTML")
        logger.info(f"Пользователь {user_id} рассчитал смету: {work} на {area} {price['unit']}")

    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Ошибка формата! Пример: <code>15, штукатурка</code>",
            reply_markup=cancel_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=main_menu())
        logger.error(f"Ошибка при расчете сметы для {user_id}: {str(e)}")


@bot.message_handler(func=lambda message: message.text == "🧮 Калькулятор материалов")
def material_calculator(message):
    if spam_protection.is_spam(message.from_user.id):
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("Плитка", "Кирпич", "Газоблок", "Назад")
    user_states[message.from_user.id] = {
        "mode": "material_choice",
        "last_activity": datetime.now()
    }
    bot.send_message(message.chat.id, "Выберите материал:", reply_markup=markup)


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "material_choice")
def handle_material_choice(message):
    material = message.text.lower()
    if material == "назад":
        return start(message)

    if material not in MATERIALS:
        bot.send_message(message.chat.id, "❌ Выберите материал из списка", reply_markup=main_menu())
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    types_list = list(MATERIALS[material].keys())
    markup.add(*types_list, "Назад")

    user_states[message.from_user.id] = {
        "mode": "material_type",
        "material": material
    }

    bot.send_message(
        message.chat.id,
        f"Выберите тип {material}:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "material_type")
def handle_material_type(message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if message.text.lower() == "назад":
        return material_calculator(message)

    if message.text not in MATERIALS[state["material"]]:
        bot.send_message(message.chat.id, "❌ Выберите тип из списка")
        return

    user_states[user_id] = {
        "mode": "material_calc",
        "material": state["material"],
        "type": message.text
    }

    bot.send_message(
        message.chat.id,
        f"Введите площадь в м² для {state['material']} ({message.text}):",
        reply_markup=types.ReplyKeyboardRemove()
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "material_calc")
def calculate_material(message):
    try:
        user_id = message.from_user.id
        state = user_states[user_id]
        area = float(message.text)

        params = MATERIALS[state["material"]][state["type"]]

        if state["material"] == "плитка":
            tiles_per_m2 = 1 / params["size"]
            total = area * tiles_per_m2 * (1 + params["waste"] / 100)
            result = f"🔹 Нужно {total:.0f} шт плитки {state['type']}"
        else:
            total = area * params["count"] * (1 + params["waste"] / 100)
            result = f"🔹 Нужно {total:.0f} шт {state['material']} ({state['type']})"

        bot.send_message(
            message.chat.id,
            f"🧮 Результат:\nПлощадь: {area} м²\nЗапас: {params['waste']}%\n{result}",
            reply_markup=main_menu()
        )
        logger.info(f"Пользователь {user_id} рассчитал материалы: {state['material']} {state['type']} на {area} м²")
        user_states.pop(user_id, None)

    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число!", reply_markup=main_menu())
        logger.warning(f"Пользователь {user_id} ввел не число для расчета материалов")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=main_menu())
        logger.error(f"Ошибка при расчете материалов для {user_id}: {str(e)}")
        user_states.pop(user_id, None)


@bot.message_handler(func=lambda m: m.text == "📩 Оставить заявку")
def request(message):
    if spam_protection.is_spam(message.from_user.id):
        return

    if check_session_timeout(message.from_user.id):
        bot.send_message(message.chat.id, "⏰ Сессия истекла. Начните заново.")
        return start(message)

    user_states[message.from_user.id] = {
        "mode": "request_contact",
        "request_data": {},
        "last_activity": datetime.now()
    }
    bot.send_message(
        message.chat.id,
        "📝 Шаг 1/3: Введите ваши контактные данные (имя и телефон)\n"
        "Пример: <i>Иван, +79991234567</i>",
        reply_markup=cancel_menu(),
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "request_contact")
def process_contact(message):
    user_states[message.from_user.id] = {
        "mode": "request_description",
        "request_data": {
            "contact": message.text
        }
    }
    bot.send_message(
        message.chat.id,
        "📝 Шаг 2/3: Опишите работу, которую нужно выполнить\n"
        "Пример: <i>Шпатлевание стен 40 м²</i>",
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "request_contact")
def process_contact(message):
    user_id = message.from_user.id

    # Валидация контактных данных
    contact = message.text.strip()
    if len(contact) < 5 or ',' not in contact:
        bot.send_message(
            message.chat.id,
            "❌ <b>Неверный формат!</b>\n\n"
            "Введите имя и телефон через запятую:\n"
            "<i>Иван, +79991234567</i>",
            parse_mode="HTML"
        )
        return

    user_states[user_id] = {
        "mode": "request_description",
        "request_data": {"contact": contact},
        "last_activity": datetime.now()
    }

    bot.send_message(
        message.chat.id,
        "📝 <b>Шаг 2/3</b>\n\n"
        "Опишите работу, которую нужно выполнить:",
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "request_description")
def process_description(message):
    user_states[message.from_user.id] = {
        "mode": "request_deadline",
        "request_data": {
            **user_states[message.from_user.id]["request_data"],
            "description": message.text
        }
    }
    bot.send_message(
        message.chat.id,
        "📝 Шаг 3/3: Укажите желаемые сроки выполнения\n"
        "Пример: <i>К 15 июня</i>",
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "request_deadline")
def process_deadline(message):
    try:
        user_id = message.from_user.id
        if user_id not in user_states:
            bot.send_message(message.chat.id, "❌ Ошибка сессии. Начните заново.", reply_markup=main_menu())
            return

        request_data = user_states[user_id]["request_data"]
        request_data["deadline"] = message.text

        # Валидация данных
        if not request_data.get("contact") or not request_data.get("description"):
            bot.send_message(message.chat.id, "❌ Неполные данные. Начните заново.", reply_markup=main_menu())
            user_states.pop(user_id, None)
            return

        request_text = (
            f"📋 <b>Новая заявка</b>\n\n"
            f"👤 <b>Контакт:</b> {request_data['contact']}\n"
            f"🔨 <b>Работа:</b> {request_data['description']}\n"
            f"📅 <b>Сроки:</b> {request_data['deadline']}"
        )

        user_states[user_id] = {
            "mode": "request_photo_choice",
            "request_text": request_text,
            "photos": [],
            "last_activity": datetime.now()
        }

        bot.send_message(
            message.chat.id,
            "✅ <b>Данные сохранены!</b>\n\n"
            "Хотите прикрепить фото к заявке?",
            reply_markup=request_menu(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Ошибка в process_deadline: {str(e)}")
        bot.send_message(
            message.chat.id,
            "⚠️ Произошла ошибка. Попробуйте начать заново.",
            reply_markup=main_menu()
        )
        user_states.pop(message.from_user.id, None)


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "request_photo_choice")
def handle_photo_choice(message):
    user_id = message.from_user.id
    if message.text == "📷 Прикрепить фото":
        user_states[user_id]["mode"] = "waiting_photo"
        bot.send_message(
            message.chat.id,
            "Отправьте фото (можно несколько, затем нажмите '📤 Отправить заявку')",
            reply_markup=types.ReplyKeyboardRemove()
        )
    elif message.text == "📤 Отправить без фото":
        if send_request_to_admin(
                user=message.from_user,
                request_text=user_states[user_id]["request_text"]
        ):
            bot.send_message(message.chat.id, "✅ Заявка отправлена!", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "❌ Ошибка отправки. Попробуйте позже.", reply_markup=main_menu())
        user_states.pop(user_id, None)
    elif message.text == "🔙 Назад":
        start(message)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {})

    if state.get("mode") != "waiting_photo":
        bot.send_message(message.chat.id, "📸 Пожалуйста, сначала оформите заявку", reply_markup=main_menu())
        return

    if spam_protection.is_spam(user_id):
        return

    try:
        # Проверка размера
        file_info = bot.get_file(message.photo[-1].file_id)
        if file_info.file_size > MAX_PHOTO_SIZE:
            bot.reply_to(message, f"❌ Фото слишком большое (максимум {MAX_PHOTO_SIZE // 1024 // 1024}МБ)")
            return

        # Проверка количества
        if len(state.get('photos', [])) >= MAX_PHOTOS:
            bot.reply_to(message, f"⚠️ Можно прикрепить не более {MAX_PHOTOS} фото")
            return

        # Сохранение фото
        downloaded_file = bot.download_file(file_info.file_path)
        photo_name = f"photo_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = os.path.join('requests', photo_name)

        with open(photo_path, 'wb') as f:
            f.write(downloaded_file)

        if "photos" not in state:
            user_states[user_id]["photos"] = []
        user_states[user_id]["photos"].append(photo_path)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["📤 Отправить заявку"]
        if len(user_states[user_id]['photos']) > 0:
            buttons.append("❌ Удалить последнее фото")
        buttons.append("🔙 Назад")
        markup.add(*buttons)

        bot.reply_to(
            message,
            f"📸 Фото {len(user_states[user_id]['photos'])}/{MAX_PHOTOS} сохранено",
            reply_markup=markup
        )

    except Exception as e:
        logger.error(f"Ошибка сохранения фото: {str(e)}")
        bot.reply_to(message, "❌ Не удалось сохранить фото")


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("mode") == "waiting_photo"
                                    and m.text == "📤 Отправить заявку")
def send_request_with_photos(message):
    user_id = message.from_user.id

    try:
        if user_id not in user_states or 'request_text' not in user_states[user_id]:
            bot.send_message(message.chat.id, "❌ Данные заявки не найдены", reply_markup=main_menu())
            return

        photos = user_states[user_id].get('photos', [])
        request_text = user_states[user_id]["request_text"]

        cleanup_old_files()

        success = send_request_to_admin(
            user=message.from_user,
            request_text=request_text,
            photos=photos if photos else None
        )

        # Очистка файлов в любом случае
        for photo_path in photos:
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except:
                pass

        if success:
            bot.send_message(
                message.chat.id,
                f"✅ <b>Заявка с {len(photos)} фото отправлена!</b>\n\n"
                "Мы скоро свяжемся с вами.",
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ <b>Ошибка при отправке</b>\n\n"
                "Попробуйте позже или свяжитесь с нами напрямую.",
                reply_markup=main_menu(),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Ошибка в send_request_with_photos: {str(e)}")
        bot.send_message(message.chat.id, "⚠️ Ошибка отправки", reply_markup=main_menu())
    finally:
        user_states.pop(user_id, None)

# Обработчик всех остальных текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    # Проверка таймаута сессии
    if user_id in user_states and check_session_timeout(user_id):
        bot.send_message(message.chat.id, "⏰ Сессия истекла. Начните заново.", reply_markup=main_menu())
        return start(message)

    # Обновление активности
    update_activity(user_id)

    # Проверка спама
    if spam_protection.is_spam(user_id):
        return

    # Если пользователь в каком-то режиме, но сообщение не обработано
    if user_id in user_states and user_states[user_id].get("mode"):
        bot.send_message(
            message.chat.id,
            "❓ Не понимаю команду. Используйте кнопки или нажмите '🔄 Сбросить'",
            reply_markup=main_menu()
        )
    else:
        start(message)


def periodic_cleanup():
    """Периодическая очистка старых файлов"""
    while True:
        try:
            cleanup_old_files()
            time.sleep(3600)  # Каждый час
        except Exception as e:
            logger.error(f"Ошибка в потоке очистки: {str(e)}")


if __name__ == '__main__':
    # Запуск потока очистки
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()

    # Очистка при запуске
    cleanup_old_files()
    logger.info("Бот запущен")
    print("Бот запущен...")

    try:
        bot.polling(none_stop=True, timeout=60)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.critical(f"Бот упал с ошибкой: {str(e)}")
        print(f"Бот упал с ошибкой: {e}")