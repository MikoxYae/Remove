from pyrogram import Client, filters
from database.database import add_user, count_users

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    """
    Handle /start command
    Registers new users and shows total user count
    """
    user = message.from_user
    
    # Check if user exists (safety check)
    if not user:
        return
    
    # Add user to database
    await add_user(user.id, user.first_name)
    
    # Get total user count
    total = await count_users()

    # Send welcome message
    await message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        f"✅ You are now registered.\n"
        f"📊 Total users: {total}"
    )
