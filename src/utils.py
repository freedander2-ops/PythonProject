import time
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class SpamProtection:
    """Класс для защиты от спама"""
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

def check_session_timeout(user_id, user_states, timeout_minutes):
    """Проверка таймаута сессии пользователя"""
    if user_id in user_states:
        last_activity = user_states[user_id].get('last_activity')
        if last_activity and datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
            cleanup_user_files(user_id, user_states)
            user_states.pop(user_id, None)
            return True
    return False

def update_activity(user_id, user_states):
    """Обновление времени последней активности пользователя"""
    if user_id in user_states:
        user_states[user_id]['last_activity'] = datetime.now()

def cleanup_user_files(user_id, user_states):
    """Очистка временных файлов, прикрепленных пользователем"""
    if user_id in user_states and 'photos' in user_states[user_id]:
        for photo_path in user_states[user_id]['photos']:
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {photo_path}: {e}")

def cleanup_old_files(folder='requests', lifetime_hours=24):
    """Очистка старых файлов в указанной папке"""
    try:
        now = datetime.now()
        if not os.path.exists(folder):
            return
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_time).total_seconds() > lifetime_hours * 3600:
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Ошибка при очистке старых файлов: {str(e)}")

def send_request_to_admin(bot, admin_id, user, request_text, photos=None):
    """Отправка заявки администратору"""
    try:
        user_info = (
            f"👤 <b>Клиент:</b>\n"
            f"• Имя: {user.first_name}\n"
            f"• Фамилия: {user.last_name or 'не указана'}\n"
            f"• Username: @{user.username or 'нет'}\n"
            f"• ID: {user.id}"
        )

        full_text = f"📩 <b>Новая заявка</b>\n\n{request_text}\n\n{user_info}"

        if photos:
            # Отправка первого фото с описанием
            with open(photos[0], 'rb') as photo:
                bot.send_photo(admin_id, photo, caption=full_text, parse_mode="HTML")

            # Отправка остальных фото
            for photo_path in photos[1:]:
                try:
                    with open(photo_path, 'rb') as photo:
                        bot.send_photo(admin_id, photo)
                except Exception as e:
                    logger.error(f"Ошибка отправки дополнительного фото: {str(e)}")
        else:
            bot.send_message(admin_id, full_text, parse_mode="HTML")

        return True

    except Exception as e:
        logger.error(f"Ошибка при отправке заявки админу: {str(e)}")
        return False
