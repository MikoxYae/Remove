from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

plugins = dict(root="plugins")

app = Client(
    "MyBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=plugins
)

if __name__ == "__main__":
    print("🤖 Bot Started Successfully with MongoDB Connection!")
    app.run()
  
