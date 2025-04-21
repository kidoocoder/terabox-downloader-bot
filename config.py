import os
from dotenv import load_dotenv

# Load environment variables from .env file if present (for local development)
load_dotenv()

# Pyrogram credentials
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Bot owner ID
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# MongoDB connection URI
MONGO_URI = os.environ.get("MONGO_URI")

# Force subscribe channels
CHANNEL_1 = os.environ.get("CHANNEL_1")  # Channel username without '@' or channel ID
CHANNEL_2 = os.environ.get("CHANNEL_2")  # Channel username without '@' or channel ID

# Bot settings
MAX_FREE_DOWNLOADS = 3
