# Terabox Downloader Telegram Bot

A Telegram bot for downloading videos from Terabox links directly to users' private chats.

## Features

- 📥 **Terabox Video Downloader**: Send videos directly to the user's private chat
- 🎁 **Free Usage Limit**: 3 free downloads per user
- ⭐️ **Premium System**: Manual premium user management by bot owner
- 🔐 **Force Channel Join**: Users must join 2 channels before using the bot
- 🎨 **Clean UI**: Custom welcome image and intuitive buttons

## Project Structure

```
terabox_bot/
├── main.py                  # Main bot file
├── config.py                # API keys, owner ID, channels, MONGO_URI
├── requirements.txt         # All required packages
├── Procfile                 # For Heroku process type
│
├── database/                # MongoDB logic
│   ├── __init__.py
│   ├── users.py
│   └── stats.py
│
├── utils/                   # Helper logic
│   ├── downloader.py        # Terabox download handler
│   └── ui.py                # UI buttons & layouts
│
├── assets/
│   └── START.jpg            # Welcome image
```

## Setup

### Prerequisites

- Python 3.8+
- MongoDB database (for user data storage)
- Telegram Bot Token

### Environment Variables

Create a `.env` file in the `terabox_bot` directory with the following variables:

```
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_id
MONGO_URI=your_mongodb_connection_string
CHANNEL_1=channel_username_1
CHANNEL_2=channel_username_2
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the bot:
   ```
   python -m terabox_bot.main
   ```

## Heroku Deployment

### Setup

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
   ```
   heroku login
   ```
3. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```
4. Set the Heroku Config Vars:
   ```
   heroku config:set API_ID=your_telegram_api_id
   heroku config:set API_HASH=your_telegram_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set OWNER_ID=your_telegram_id
   heroku config:set MONGO_URI=your_mongodb_connection_string
   heroku config:set CHANNEL_1=channel_username_1
   heroku config:set CHANNEL_2=channel_username_2
   heroku config:set HEROKU_APP_NAME=your-app-name
   ```
5. Deploy to Heroku:
   ```
   git push heroku main
   ```

## Bot Commands

- `/start` - Start the bot and check subscription status
- `/terabox <url>` - Download a video from Terabox link
- `/addpremium <user_id>` - Add a user as premium (Owner only)
- `/stats` - Show bot statistics (Owner only)

## License

This project is licensed under the MIT License.
