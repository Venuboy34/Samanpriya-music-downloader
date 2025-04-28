# Zero Music Bot

A Telegram bot that downloads music from YouTube and sends it back with metadata and thumbnails included.

## Features

- Download music from YouTube links
- Search for music using keywords
- Select audio quality (128kbps, 256kbps, 320kbps)
- Preserves metadata including thumbnails
- Easy to deploy on Koyeb for 24/7 operation

## Deployment Instructions for Koyeb

### Prerequisites

1. A Telegram Bot Token (obtain from [@BotFather](https://t.me/BotFather))
2. A [Koyeb](https://koyeb.com) account

### Steps to Deploy

1. **Create Your Bot**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Use the `/newbot` command and follow instructions
   - Copy your bot token

2. **Prepare Deployment Files**
   - Ensure you have all these files in your repository:
     - `bot.py` (main bot code)
     - `requirements.txt` (dependencies)
     - `Dockerfile` (container configuration)
     - `koyeb.yaml` (Koyeb configuration)

3. **Set Up on Koyeb**
   - Sign in to [Koyeb](https://app.koyeb.com/)
   - Create a new app and connect to your GitHub repository
   - Set the environment variable:
     - `BOT_TOKEN`: Your Telegram bot token
   - Deploy the service

4. **Verify Bot is Running**
   - Once deployed, message your bot on Telegram
   - Send the `/start` command to verify it's working

## Usage

- `/start` - Start the bot
- `/help` - Show help message
- `/search [query]` - Search for music
- Send any YouTube link to download directly

## Credits

Created by [@zerocreations](https://t.me/zerocreations)

## Note

This bot is for educational purposes only. Please respect copyright laws and YouTube's Terms of Service when using this bot.
