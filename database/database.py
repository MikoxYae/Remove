import motor.motor_asyncio
from config import DB_URI, DB_NAME
from datetime import datetime
from bson import ObjectId

# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
channels_col = db["channels"]
removal_tasks_col = db["removal_tasks"]

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
        "invite_link": invite_link,
        "connected_at": datetime.utcnow()
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

# ==================== REMOVAL TASK FUNCTIONS ====================

async def add_removal_task(user_id, removal_time, duration, unit):
    """Add removal task to database"""
    task_data = {
        "user_id": user_id,
        "removal_time": removal_time,
        "duration": duration,
        "unit": unit,
        "created_at": datetime.utcnow(),
        "status": "pending"
    }
    
    result = await removal_tasks_col.insert_one(task_data)
    return str(result.inserted_id)

async def get_removal_task(task_id):
    """Get removal task by ID"""
    try:
        return await removal_tasks_col.find_one({"_id": ObjectId(task_id)})
    except:
        return None

async def get_pending_tasks():
    """Get all pending removal tasks"""
    tasks = []
    async for task in removal_tasks_col.find({"status": "pending"}):
        tasks.append(task)
    return tasks

async def get_all_tasks():
    """Get all removal tasks"""
    tasks = []
    async for task in removal_tasks_col.find().sort("created_at", -1):
        tasks.append(task)
    return tasks

async def update_task_status(task_id, status):
    """Update task status"""
    try:
        await removal_tasks_col.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": {
                "status": status,
                "updated_at": datetime.utcnow()
            }}
        )
        return True
    except:
        return False

async def delete_task(task_id):
    """Delete removal task"""
    try:
        result = await removal_tasks_col.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    except:
        return False

async def get_user_tasks(user_id):
    """Get all removal tasks for a specific user"""
    tasks = []
    async for task in removal_tasks_col.find({"user_id": user_id}):
        tasks.append(task)
    return tasks

async def count_tasks():
    """Get total removal tasks count"""
    return await removal_tasks_col.count_documents({})

async def count_pending_tasks():
    """Get pending removal tasks count"""
    return await removal_tasks_col.count_documents({"status": "pending"})
