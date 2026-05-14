import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        ADMIN_ID = None

# Константы
MAX_PHOTOS = 3
MAX_PHOTO_SIZE = 15 * 1024 * 1024
PHOTO_LIFETIME_HOURS = 24
SESSION_TIMEOUT_MINUTES = 30
