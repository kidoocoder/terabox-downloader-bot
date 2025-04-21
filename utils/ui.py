from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_1, CHANNEL_2

def get_start_markup(user_id, remaining_downloads=None, is_premium=False):
    """
    Create inline keyboard for start message
    """
    buttons = [
        [
            InlineKeyboardButton("🔗 Send Terabox Link", callback_data="terabox_help"),
            InlineKeyboardButton("🧑‍💼 Contact Owner", callback_data="contact_owner")
        ]
    ]

    return InlineKeyboardMarkup(buttons)

def get_force_sub_markup():
    """
    Create force subscribe markup with channel links
    """
    # Format channel links properly
    channel1_link = f"https://t.me/{CHANNEL_1}" if not CHANNEL_1.startswith("@") and not CHANNEL_1.startswith("-100") else f"https://t.me/{CHANNEL_1.replace('@', '')}"
    channel2_link = f"https://t.me/{CHANNEL_2}" if not CHANNEL_2.startswith("@") and not CHANNEL_2.startswith("-100") else f"https://t.me/{CHANNEL_2.replace('@', '')}"

    buttons = [
        [
            InlineKeyboardButton("Channel 1 🔔", url=channel1_link),
            InlineKeyboardButton("Channel 2 🔔", url=channel2_link)
        ],
        [
            InlineKeyboardButton("✅ I've Joined", callback_data="check_subscription")
        ]
    ]

    return InlineKeyboardMarkup(buttons)

def get_terabox_help_markup():
    """
    Create help markup for terabox command
    """
    buttons = [
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_start")
        ]
    ]

    return InlineKeyboardMarkup(buttons)

def format_remaining_downloads(remaining, is_premium=False):
    """
    Format text showing remaining downloads or premium status
    """
    if is_premium:
        return "🌟 You have *Premium* status with *unlimited* downloads!"
    else:
        return f"📊 You have *{remaining}* free download{'s' if remaining != 1 else ''} remaining."
