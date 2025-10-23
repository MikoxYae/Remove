import motor.motor_asyncio
from config import DB_URI, DB_NAME

# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

# Example user collection
users_col = db["users"]

async def add_user(user_id, name):
    user = await users_col.find_one({"_id": user_id})
    if not user:
        await users_col.insert_one({"_id": user_id, "name": name})
        return True
    return False

async def get_user(user_id):
    return await users_col.find_one({"_id": user_id})

async def count_users():
    return await users_col.count_documents({})
