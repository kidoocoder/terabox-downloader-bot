import os
from dotenv import load_dotenv

# Load environment variables from .env file if present (for local development)
load_dotenv()

# Pyrogram credentials
API_ID = int(os.environ.get("API_ID", 26169983))
API_HASH = os.environ.get("API_HASH", "c69f585ca5aee54e14c04cb02607d679")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7700343108:AAG6E7jCaY3ERdkKb1goy8a21hiIZYrLEXo")

# Bot owner ID
OWNER_ID = int(os.environ.get("OWNER_ID", 7767099543))

# MongoDB connection URI
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://KingOfHell:Highspeedorg@cluster0.ha2cc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Force subscribe channels
CHANNEL_1 = os.environ.get("CHANNEL_1", "Guppppp_Shuppppp")
CHANNEL_2 = os.environ.get("CHANNEL_2", "SYNTAX_WORLD")  # Channel username without '@' or channel ID


# Bot settings
MAX_FREE_DOWNLOADS = 50
