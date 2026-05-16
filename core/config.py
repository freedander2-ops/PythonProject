import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Logger setup
logger = logging.getLogger('PythonProject')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler
file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        logger.warning("Invalid ADMIN_ID in .env, should be an integer")
        ADMIN_ID = None

# Operational Constants
MAX_PHOTOS = 3
MAX_PHOTO_SIZE = 15 * 1024 * 1024
PHOTO_LIFETIME_HOURS = 24
SESSION_TIMEOUT_MINUTES = 30

# Path settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUESTS_DIR = os.path.join(BASE_DIR, 'requests')

os.makedirs(REQUESTS_DIR, exist_ok=True)
