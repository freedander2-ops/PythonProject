import logging

logger = logging.getLogger(__name__)

def format_application_for_admin(user_info: dict, app_data: dict) -> str:
    """Форматирование текста заявки для администратора"""
    text = (
        f"📩 <b>Новая заявка</b>\n\n"
        f"👤 <b>Клиент:</b>\n"
        f"• Имя: {user_info.get('first_name')}\n"
        f"• Username: @{user_info.get('username', 'нет')}\n"
        f"• Контакты: {app_data.get('contact')}\n\n"
        f"🛠 <b>Работа:</b> {app_data.get('description')}\n"
        f"📅 <b>Сроки:</b> {app_data.get('deadline')}"
    )
    return text

def send_application(bot, admin_id: int, text: str, photos: list = None) -> bool:
    """Отправка заявки администратору через бота"""
    try:
        if not admin_id:
            logger.error("ADMIN_ID not configured")
            return False

        if photos:
            with open(photos[0], 'rb') as photo:
                bot.send_photo(admin_id, photo, caption=text, parse_mode="HTML")
            for photo_path in photos[1:]:
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(admin_id, photo)
        else:
            bot.send_message(admin_id, text, parse_mode="HTML")
        return True
    except Exception as e:
        logger.error(f"Failed to send application to admin: {e}")
        return False
