from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import add_channel, add_removal_task, get_all_channels
from config import OWNER_ID
import asyncio
from datetime import datetime, timedelta

@Client.on_message(filters.command("connect") & filters.user(OWNER_ID))
async def connect_channel(client: Client, message: Message):
    """
    Command: /connect Channel Name Invite Link
    Example: /connect Snap Premium 2 https://t.me/+ZVM9bS0OLWZjZTQ1
    """
    
    # Check if command has correct format
    if len(message.command) < 3:
        await message.reply_text(
            "❌ **Invalid format!**\n\n"
            "**Usage:**\n"
            "`/connect Channel Name Invite Link`\n\n"
            "**Example:**\n"
            "`/connect Snap Premium 2 https://t.me/+ZVM9bS0OLWZjZTQ1`"
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
    
    try:
        # Wait for forwarded message with 60 second timeout
        forwarded_msg = await client.listen(
            message.chat.id,
            timeout=60
        )
        
        # Check if message is forwarded
        if not forwarded_msg.forward_origin:
            await waiting_msg.delete()
            await message.reply_text("❌ Please forward a message!")
            return
        
        # Extract channel ID based on forward origin type
        channel_id = None
        
        # Try to get channel from forward_origin
        if hasattr(forwarded_msg.forward_origin, 'chat'):
            channel_id = forwarded_msg.forward_origin.chat.id
        elif hasattr(forwarded_msg.forward_origin, 'sender_chat'):
            channel_id = forwarded_msg.forward_origin.sender_chat.id
        
        if not channel_id:
            await waiting_msg.delete()
            await message.reply_text("❌ Could not extract channel ID. Please forward a message from a channel!")
            return
        
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
    
    except Exception as e:
        await waiting_msg.delete()
        await message.reply_text(f"❌ **Error occurred:**\n`{str(e)}`\n\nPlease send screenshot to developer.")


@Client.on_message(filters.command("remove") & filters.user(OWNER_ID))
async def schedule_removal(client: Client, message: Message):
    """
    Command: /remove user_id duration unit
    Examples: 
    - /remove 1260762308 30 d  (remove in 30 days)
    - /remove 1260762308 30 s  (remove in 30 seconds)
    - /remove 1260762308 30 m  (remove in 30 minutes)
    - /remove 1260762308 30 h  (remove in 30 hours)
    """
    
    # Check if command has correct format
    if len(message.command) != 4:
        await message.reply_text(
            "❌ **Invalid format!**\n\n"
            "**Usage:**\n"
            "`/remove user_id duration unit`\n\n"
            "**Examples:**\n"
            "`/remove 1260762308 30 d` (30 days)\n"
            "`/remove 1260762308 30 h` (30 hours)\n"
            "`/remove 1260762308 30 m` (30 minutes)\n"
            "`/remove 1260762308 30 s` (30 seconds)\n\n"
            "**Units:** s=seconds, m=minutes, h=hours, d=days"
        )
        return
    
    try:
        # Parse command arguments
        user_id = int(message.command[1])
        duration = int(message.command[2])
        unit = message.command[3].lower()
        
        # Validate unit
        if unit not in ['s', 'm', 'h', 'd']:
            await message.reply_text("❌ Invalid time unit! Use: s (seconds), m (minutes), h (hours), d (days)")
            return
        
        # Validate duration
        if duration <= 0:
            await message.reply_text("❌ Duration must be greater than 0!")
            return
        
        # Calculate removal time
        now = datetime.utcnow()
        
        if unit == 's':
            removal_time = now + timedelta(seconds=duration)
            unit_text = "seconds"
        elif unit == 'm':
            removal_time = now + timedelta(minutes=duration)
            unit_text = "minutes"
        elif unit == 'h':
            removal_time = now + timedelta(hours=duration)
            unit_text = "hours"
        elif unit == 'd':
            removal_time = now + timedelta(days=duration)
            unit_text = "days"
        
        # Get all connected channels
        channels = await get_all_channels()
        
        if not channels:
            await message.reply_text("❌ No channels connected! Use `/connect` to add channels first.")
            return
        
        # Save removal task to database
        task_id = await add_removal_task(user_id, removal_time, duration, unit)
        
        # Schedule the removal task
        asyncio.create_task(execute_removal(client, user_id, removal_time, task_id))
        
        # Send confirmation message
        await message.reply_text(
            f"⏰ **Removal Scheduled!**\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"⏱️ **Duration:** {duration} {unit_text}\n"
            f"🕒 **Removal Time:** {removal_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"📺 **Channels:** {len(channels)} connected channel(s)\n\n"
            f"✅ User will be removed from all connected channels automatically."
        )
        
    except ValueError:
        await message.reply_text("❌ Invalid user_id or duration! Please use numbers only.")
    except Exception as e:
        await message.reply_text(f"❌ **Error occurred:**\n`{str(e)}`")


async def execute_removal(client: Client, user_id: int, removal_time: datetime, task_id: str):
    """
    Execute the removal task at the scheduled time
    """
    try:
        # Calculate wait time
        now = datetime.utcnow()
        wait_seconds = (removal_time - now).total_seconds()
        
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        
        # Get all connected channels
        channels = await get_all_channels()
        
        success_count = 0
        failed_count = 0
        
        for channel in channels:
            try:
                channel_id = channel['_id']
                
                # Try to ban/kick user from channel
                await client.ban_chat_member(
                    chat_id=channel_id,
                    user_id=user_id
                )
                
                # Optionally unban immediately (just kick, not permanent ban)
                await asyncio.sleep(1)
                await client.unban_chat_member(
                    chat_id=channel_id,
                    user_id=user_id
                )
                
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                print(f"Failed to remove user {user_id} from channel {channel_id}: {str(e)}")
        
        # Send notification to owner
        try:
            await client.send_message(
                chat_id=OWNER_ID,
                text=f"✅ **Removal Completed!**\n\n"
                     f"👤 **User ID:** `{user_id}`\n"
                     f"✅ **Removed from:** {success_count} channel(s)\n"
                     f"❌ **Failed:** {failed_count} channel(s)\n"
                     f"🕒 **Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
        except:
            pass
            
    except Exception as e:
        print(f"Error in execute_removal: {str(e)}")
