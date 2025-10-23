from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import add_channel, get_channel
from config import OWNER_ID
import asyncio

@Client.on_message(filters.command("connect") & filters.user(OWNER_ID))
async def connect_channel(client: Client, message: Message):
    # Check if command has correct format
    if len(message.command) < 3:
        await message.reply_text(
            "❌ Invalid format!\n\n"
            "**Usage:**\n"
            "`/connect Channel Name Invite Link`\n\n"
            "**Example:**\n"
            "`/connect Snap premium 2 https://t.me/+4fteb1Teqh8wODVl`"
        )
        return
    
    # Parse command arguments
    args = message.text.split(maxsplit=1)[1]  # Get everything after /connect
    parts = args.rsplit(' ', 1)  # Split from right to get last part as link
    
    if len(parts) != 2:
        await message.reply_text("❌ Please provide both channel name and invite link!")
        return
    
    channel_name = parts[0].strip()
    invite_link = parts[1].strip()
    
    # Validate invite link
    if not (invite_link.startswith('https://t.me/') or invite_link.startswith('http://t.me/')):
        await message.reply_text("❌ Invalid Telegram invite link!")
        return
    
    # Send waiting message
    waiting_msg = await message.reply_text(
        f"📺 **Setting up channel connection for:**\n"
        f"{channel_name}\n\n"
        f"👆 Please forward any message from the channel you want to connect to this bot.\n\n"
        f"⏱️ **Waiting for forwarded message...**\n"
        f"Timeout: 60 seconds"
    )
    
    # Wait for forwarded message
    def check_forward(_, __, m: Message):
        return (
            m.from_user.id == OWNER_ID and 
            m.forward_from_chat is not None and
            m.forward_from_chat.type == "channel"
        )
    
    try:
        # Wait for forwarded message with 60 second timeout
        forwarded_msg = await client.listen(
            message.chat.id,
            filters=filters.create(check_forward),
            timeout=60
        )
        
        # Extract channel ID
        channel_id = forwarded_msg.forward_from_chat.id
        
        # Save to database
        await add_channel(channel_id, channel_name, invite_link)
        
        # Delete waiting message
        await waiting_msg.delete()
        
        # Send success message
        await message.reply_text(
            f"🎉 **Channel Connected Successfully!**\n\n"
            f"📺 **Channel Name:** {channel_name}\n"
            f"🔗 **Channel ID:** `{channel_id}`\n"
            f"🔗 **Channel Invite Link:** {invite_link}"
        )
        
    except asyncio.TimeoutError:
        await waiting_msg.edit_text(
            "⏱️ **Timeout!**\n\n"
            "You didn't forward any message within 60 seconds.\n"
            "Please try again with `/connect` command."
        )
