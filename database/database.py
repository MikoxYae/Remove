import motor.motor_asyncio
from config import DB_URI, DB_NAME

# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
channels_col = db["channels"]

# ==================== USER FUNCTIONS ====================

async def add_user(user_id, name):
    """Add new user to database"""
    user = await users_col.find_one({"_id": user_id})
    if not user:
        await users_col.insert_one({"_id": user_id, "name": name})
        return True
    return False

async def get_user(user_id):
    """Get user details by ID"""
    return await users_col.find_one({"_id": user_id})

async def count_users():
    """Get total user count"""
    return await users_col.count_documents({})

async def get_all_users():
    """Get all users"""
    users = []
    async for user in users_col.find():
        users.append(user)
    return users

async def delete_user(user_id):
    """Remove user from database"""
    result = await users_col.delete_one({"_id": user_id})
    return result.deleted_count > 0

async def update_user(user_id, data):
    """Update user information"""
    await users_col.update_one(
        {"_id": user_id},
        {"$set": data}
    )
    return True

# ==================== CHANNEL FUNCTIONS ====================

async def add_channel(channel_id, channel_name, invite_link):
    """Add or update channel in database"""
    channel_data = {
        "_id": channel_id,
        "name": channel_name,
        "invite_link": invite_link
    }
    
    # Update if exists, insert if new
    await channels_col.update_one(
        {"_id": channel_id},
        {"$set": channel_data},
        upsert=True
    )
    return True

async def get_channel(channel_id):
    """Get channel details by ID"""
    return await channels_col.find_one({"_id": channel_id})

async def get_all_channels():
    """Get all connected channels"""
    channels = []
    async for channel in channels_col.find():
        channels.append(channel)
    return channels

async def delete_channel(channel_id):
    """Remove channel from database"""
    result = await channels_col.delete_one({"_id": channel_id})
    return result.deleted_count > 0

async def count_channels():
    """Get total channel count"""
    return await channels_col.count_documents({})

async def channel_exists(channel_id):
    """Check if channel exists in database"""
    channel = await channels_col.find_one({"_id": channel_id})
    return channel is not None
