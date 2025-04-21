from database import stats_collection, users_collection

async def increment_downloads_stat():
    """
    Increment total downloads count
    """
    await stats_collection.update_one(
        {"_id": "stats"},
        {"$inc": {"total_downloads": 1}},
        upsert=True
    )

async def get_stats():
    """
    Get bot statistics
    """
    # Get stats from stats collection
    stats = await stats_collection.find_one({"_id": "stats"})
    if not stats:
        stats = {"total_downloads": 0}

    # Count total users
    total_users = await users_collection.count_documents({})

    # Count premium users
    premium_users = await users_collection.count_documents({"is_premium": True})

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_downloads": stats.get("total_downloads", 0)
    }
