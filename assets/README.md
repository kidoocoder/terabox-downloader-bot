# Assets Directory

This directory contains static assets used by the Terabox Downloader Bot.

## Required Files

### START.jpg
This is the welcome image displayed when users start the bot. It should be:
- Named exactly `START.jpg`
- Recommended resolution: 800x450 pixels
- Maximum file size: 5MB (Telegram limit)

If this file is not present, the bot will attempt to download a placeholder image on startup, but it's recommended to provide your own custom image here for a more professional look.

## Usage

The bot automatically loads these assets using the correct file paths. Don't rename the files or move them to a different location unless you update the corresponding file paths in the code.
