from database import users_collection
from config import MAX_FREE_DOWNLOADS

async def get_user(user_id: int):
    """
    Get user data from database
    """
    user = await users_collection.find_one({"_id": user_id})
    if not user:
        # Initialize user if not exists
        user = {
            "_id": user_id,
            "downloads": 0,
            "is_premium": False,
            "joined_date": None
        }
        await users_collection.insert_one(user)
    return user

async def increment_downloads(user_id: int):
    """
    Increment user's download count by 1
    """
    await users_collection.update_one(
        {"_id": user_id},
        {"$inc": {"downloads": 1}}
    )

async def get_downloads_count(user_id: int):
    """
    Get user's download count
    """
    user = await get_user(user_id)
    return user.get("downloads", 0)

async def set_premium(user_id: int, status: bool = True):
    """
    Set user's premium status
    """
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_premium": status}}
    )

async def is_premium(user_id: int):
    """
    Check if user is premium
    """
    user = await get_user(user_id)
    return user.get("is_premium", False)

async def can_download(user_id: int):
    """
    Check if user can download (premium or has free downloads left)
    """
    user = await get_user(user_id)

    # Premium users can always download
    if user.get("is_premium", False):
        return True

    # Free users have limited downloads
    return user.get("downloads", 0) < MAX_FREE_DOWNLOADS

async def get_remaining_downloads(user_id: int):
    """
    Get remaining free downloads for a user
    """
    user = await get_user(user_id)

    # Premium users have unlimited downloads
    if user.get("is_premium", False):
        return float('inf')

    downloads = user.get("downloads", 0)
    return max(0, MAX_FREE_DOWNLOADS - downloads)

async def record_user_join(user_id: int):
    """
    Record when a user joins (passes force subscribe)
    """
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"joined_date": True}},
        upsert=True
    )
