import telebot
import threading
import time
from core.config import API_TOKEN, PHOTO_LIFETIME_HOURS, REQUESTS_DIR, logger
from bot.handlers import register_handlers
from utils.helpers import cleanup_old_files

def run_bot():
    if not API_TOKEN:
        logger.critical("API_TOKEN is missing!")
        return

    bot = telebot.TeleBot(API_TOKEN)
    register_handlers(bot)

    def scheduler():
        while True:
            cleanup_old_files(REQUESTS_DIR, PHOTO_LIFETIME_HOURS)
            time.sleep(3600)

    threading.Thread(target=scheduler, daemon=True).start()

    logger.info("Bot infrastructure started")
    print("🚀 Bot is running in modular mode...")

    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        logger.error(f"Polling error: {e}")
        time.sleep(5)
        run_bot()

if __name__ == "__main__":
    run_bot()
