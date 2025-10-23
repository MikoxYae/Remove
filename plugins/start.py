from pyrogram import Client, filters
from database.database import add_user, count_users

@Client.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    await add_user(user.id, user.first_name)
    total = await count_users()

    await message.reply_text(
        f"👋 Hello {user.first_name}!\n\n✅ You are now registered.\n📊 Total users: {total}"
    )
