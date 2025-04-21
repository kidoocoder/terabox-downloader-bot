from pymongo import MongoClient
from config import MONGO_URI

# Initialize MongoDB client
client = MongoClient(MONGO_URI)

# Create database for our bot
db = client["terabox_bot"]

# Collections
users_collection = db["users"]
stats_collection = db["stats"]
