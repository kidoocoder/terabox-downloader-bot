import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup,
    InlineKeyboardButton, BotCommand
)
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid

# Import config and modules
from config import (
    API_ID, API_HASH, BOT_TOKEN, OWNER_ID,
    CHANNEL_1, CHANNEL_2, MAX_FREE_DOWNLOADS
)
from database import users
from database import stats
from utils.downloader import TeraboxDownloader
from utils.ui import (
    get_start_markup, get_force_sub_markup, get_terabox_help_markup,
    format_remaining_downloads
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the client
app = Client(
    "terabox_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Command set for the bot
BOT_COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("terabox", "Download video from Terabox link"),
    BotCommand("stats", "Get bot statistics (Owner only)"),
    BotCommand("addpremium", "Add a premium user (Owner only)")
]

# Set the commands list
async def setup_commands():
    await app.set_bot_commands(BOT_COMMANDS)

# Helper function to check if user is subscribed to both channels
async def is_user_subscribed(user_id):
    try:
        for channel in [CHANNEL_1, CHANNEL_2]:
            chat_id = channel if channel.startswith('-100') else f'@{channel.replace("@", "")}'
            await app.get_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except (UserNotParticipant, ChatAdminRequired, PeerIdInvalid) as e:
        logger.info(f"User {user_id} not subscribed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return True

# Force subscribe middleware
async def force_subscribe(message, user_id=None):
    user_id = user_id or message.from_user.id

    if not await is_user_subscribed(user_id):
        if isinstance(message, Message):
            await message.reply(
                "⚠️ **You need to join our channels before using this bot!**\n\n"
                "Please join both channels and click \"I've Joined\" button.",
                reply_markup=get_force_sub_markup()
            )
        elif isinstance(message, CallbackQuery):
            await message.answer(
                "⚠️ **You need to join our channels before using this bot!**\n\n"
                "Please join both channels and click \"I've Joined\" button.",
                show_alert=True
            )
            await message.message.edit_text(
                "⚠️ **You need to join our channels before using this bot!**\n\n"
                "Please join both channels and click \"I've Joined\" button.",
                reply_markup=get_force_sub_markup()
            )
        return False
    return True

# Start command handler
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    user_id = message.from_user.id

    if not await force_subscribe(message):
        return

    await users.record_user_join(user_id)
    is_premium_user = await users.is_premium(user_id)
    remaining = await users.get_remaining_downloads(user_id)
    status_text = format_remaining_downloads(remaining, is_premium_user)
    start_image_path = os.path.join(os.path.dirname(__file__), "assets", "START.jpg")

    if os.path.exists(start_image_path):
        await message.reply_photo(
            photo=start_image_path,
            caption=(
                "👋 **Welcome to Terabox Downloader Bot!**\n\n"
                "I can help you download videos from Terabox links.\n"
                f"{status_text}\n\n"
                "Use /terabox command followed by a Terabox link to download videos."
            ),
            reply_markup=get_start_markup(user_id, remaining, is_premium_user)
        )
    else:
        await message.reply_text(
            "👋 **Welcome to Terabox Downloader Bot!**\n\n"
            "I can help you download videos from Terabox links.\n"
            f"{status_text}\n\n"
            "Use /terabox command followed by a Terabox link to download videos.",
            reply_markup=get_start_markup(user_id, remaining, is_premium_user)
        )

# Terabox command handler
@app.on_message(filters.command("terabox") & filters.private)
async def terabox_command(client, message):
    user_id = message.from_user.id

    if not await force_subscribe(message):
        return

    if not await users.can_download(user_id):
        await message.reply_text(
            "❌ **You've used your 3 free downloads. Please contact the owner to get premium access.**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧑‍💼 Contact Owner", callback_data="contact_owner")]
            ])
        )
        return

    if len(message.command) < 2:
        await message.reply_text(
            "❌ **You need to provide a Terabox link!**\n\n"
            "Use the command like this:\n"
            "`/terabox https://terabox.com/your-link`"
        )
        return

    url = message.command[1]

    if not TeraboxDownloader.is_valid_terabox_url(url):
        await message.reply_text(
            "❌ **Invalid Terabox URL!**\n\n"
            "Please make sure you're using a valid Terabox link."
        )
        return

    processing_msg = await message.reply_text(
        "⏳ **Processing your Terabox link...**"
    )

    try:
        last_edit_time = 0

        async def progress_callback(progress):
            nonlocal last_edit_time
            current_time = asyncio.get_event_loop().time()
            if current_time - last_edit_time >= 3:
                try:
                    await processing_msg.edit_text(
                        f"⏳ **Downloading video... {progress:.1f}%**"
                    )
                    last_edit_time = current_time
                except Exception:
                    pass

        file_path, error = await TeraboxDownloader.download_video(url, progress_callback)

        if not file_path or error:
            await processing_msg.edit_text(
                f"❌ **Download failed!**\n\n"
                f"Error: {error}"
            )
            return

        await processing_msg.edit_text("⌛ **Download complete! Sending video...**")

        try:
            await message.reply_video(
                video=file_path,
                caption=f"🎬 **Here's your video from Terabox!**\n\nRequested by: {message.from_user.mention}",
                supports_streaming=True
            )

            await users.increment_downloads(user_id)
            await stats.increment_downloads_stat()
            await processing_msg.delete()

        except Exception as e:
            await processing_msg.edit_text(
                f"❌ **Failed to send video!**\n\n"
                f"Error: {str(e)}"
            )

        try:
            os.unlink(file_path)
        except:
            pass

    except Exception as e:
        await processing_msg.edit_text(
            f"❌ **An error occurred!**\n\n"
            f"Error: {str(e)}"
        )

# Add premium user command (Owner only)
@app.on_message(filters.command("addpremium") & filters.private & filters.user(OWNER_ID))
async def add_premium_command(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **You need to provide a user ID!**\n\n"
            "Use the command like this:\n"
            "`/addpremium 123456789`"
        )
        return

    try:
        user_id = int(message.command[1])
        await users.set_premium(user_id, True)
        await message.reply_text(
            f"✅ **User {user_id} has been added as a premium user!**"
        )
        try:
            await client.send_message(
                chat_id=user_id,
                text="🌟 **Congratulations!**\n\n"
                     "You have been upgraded to **Premium** status!\n"
                     "You now have unlimited downloads from Terabox."
            )
        except:
            await message.reply_text(
                "Note: Could not notify the user about their premium status."
            )
    except ValueError:
        await message.reply_text(
            "❌ **Invalid user ID! Please provide a valid numeric ID.**"
        )
    except Exception as e:
        await message.reply_text(
            f"❌ **An error occurred!**\n\n"
            f"Error: {str(e)}"
        )

# Stats command (Owner only)
@app.on_message(filters.command("stats") & filters.private & filters.user(OWNER_ID))
async def stats_command(client, message):
    bot_stats = await stats.get_stats()
    await message.reply_text(
        "📊 **Bot Statistics**\n\n"
        f"👥 Total Users: `{bot_stats['total_users']}`\n"
        f"🌟 Premium Users: `{bot_stats['premium_users']}`\n"
        f"🎬 Total Downloads: `{bot_stats['total_downloads']}`"
    )

# Callback query handler for inline buttons
@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "check_subscription":
        if await is_user_subscribed(user_id):
            await users.record_user_join(user_id)
            is_premium_user = await users.is_premium(user_id)
            remaining = await users.get_remaining_downloads(user_id)
            status_text = format_remaining_downloads(remaining, is_premium_user)
            start_image_path = os.path.join(os.path.dirname(__file__), "assets", "START.jpg")

            if os.path.exists(start_image_path):
                await callback_query.message.delete()
                await callback_query.message.reply_photo(
                    photo=start_image_path,
                    caption=(
                        "👋 **Welcome to Terabox Downloader Bot!**\n\n"
                        "I can help you download videos from Terabox links.\n"
                        f"{status_text}\n\n"
                        "Use /terabox command followed by a Terabox link to download videos."
                    ),
                    reply_markup=get_start_markup(user_id, remaining, is_premium_user)
                )
            else:
                await callback_query.message.edit_text(
                    "👋 **Welcome to Terabox Downloader Bot!**\n\n"
                    "I can help you download videos from Terabox links.\n"
                    f"{status_text}\n\n"
                    "Use /terabox command followed by a Terabox link to download videos.",
                    reply_markup=get_start_markup(user_id, remaining, is_premium_user)
                )
            await callback_query.answer("✅ Subscription verified! You can now use the bot.", show_alert=True)
        else:
            await callback_query.answer("❌ You haven't joined both channels yet!", show_alert=True)

    elif data == "terabox_help":
        await callback_query.message.edit_text(
            "🔗 **How to Download from Terabox**\n\n"
            "1. Copy a Terabox video link\n"
            "2. Send it to me using command:\n"
            "   `/terabox <your_terabox_link>`\n\n"
            "I'll download and send the video directly to you!",
            reply_markup=get_terabox_help_markup()
        )
        await callback_query.answer()

    elif data == "contact_owner":
        await callback_query.message.edit_text(
            "🧑‍💼 **Contact the Bot Owner**\n\n"
            f"To get premium access with unlimited downloads, "
            f"please contact the bot owner:\n\n"
            f"👤 @username or [Click here](tg://user?id={OWNER_ID})\n\n"
            f"Premium gives you unlimited downloads from Terabox!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_start")]
            ]),
            disable_web_page_preview=True
        )
        await callback_query.answer()

    elif data == "back_to_start":
        if not await force_subscribe(callback_query, user_id):
            return

        is_premium_user = await users.is_premium(user_id)
        remaining = await users.get_remaining_downloads(user_id)
        status_text = format_remaining_downloads(remaining, is_premium_user)
        start_image_path = os.path.join(os.path.dirname(__file__), "assets", "START.jpg")

        if os.path.exists(start_image_path) and callback_query.message.photo:
            await callback_query.message.edit_caption(
                caption=(
                    "👋 **Welcome to Terabox Downloader Bot!**\n\n"
                    "I can help you download videos from Terabox links.\n"
                    f"{status_text}\n\n"
                    "Use /terabox command followed by a Terabox link to download videos."
                ),
                reply_markup=get_start_markup(user_id, remaining, is_premium_user)
            )
        else:
            await callback_query.message.edit_text(
                "👋 **Welcome to Terabox Downloader Bot!**\n\n"
                "I can help you download videos from Terabox links.\n"
                f"{status_text}\n\n"
                "Use /terabox command followed by a Terabox link to download videos.",
                reply_markup=get_start_markup(user_id, remaining, is_premium_user)
            )
        await callback_query.answer()

# Create a test START.jpg file in assets folder
async def create_test_start_image():
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    start_image_path = os.path.join(assets_dir, "START.jpg")

    if not os.path.exists(start_image_path):
        try:
            os.makedirs(assets_dir, exist_ok=True)
            import urllib.request
            placeholder_url = "https://via.placeholder.com/800x450.jpg?text=TERABOX+DOWNLOADER+BOT"
            urllib.request.urlretrieve(placeholder_url, start_image_path)
            logger.info(f"Created placeholder START.jpg at {start_image_path}")
        except Exception as e:
            logger.error(f"Failed to create placeholder image: {e}")

# Check if bot is running on Heroku and set webhook if needed
async def setup_webhook():
    heroku_app_name = os.environ.get("HEROKU_APP_NAME")
    if heroku_app_name:
        webhook_url = f"https://{heroku_app_name}.herokuapp.com/{BOT_TOKEN}"
        await app.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")

# Main entry point
if __name__ == "__main__":
    # Run initialization tasks before starting the bot
    with app:
        app.loop.run_until_complete(setup_commands())
        app.loop.run_until_complete(create_test_start_image())
        app.loop.run_until_complete(setup_webhook())
        logger.info("Bot initialization complete!")
    app.run()
