import os
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class SpamProtection:
    """Защита от спама на основе временных окон"""
    def __init__(self, max_messages=5, time_window=60):
        self.user_messages = defaultdict(list)
        self.max_messages = max_messages
        self.time_window = time_window

    def is_spam(self, user_id: int) -> bool:
        now = time.time()
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < self.time_window
        ]

        if len(self.user_messages[user_id]) >= self.max_messages:
            return True

        self.user_messages[user_id].append(now)
        return False

    def clear_user(self, user_id: int):
        self.user_messages.pop(user_id, None)

def cleanup_files(file_paths: list):
    """Удаление списка файлов"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")

def cleanup_old_files(folder: str, lifetime_hours: int):
    """Очистка файлов старше определенного времени"""
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
        logger.error(f"Error during scheduled file cleanup: {e}")
