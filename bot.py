import os
import logging
import asyncio
import yt_dlp
import aiohttp
import eyed3
from PIL import Image
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment variables for security
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7450474840:AAGU-qhoDcbDZWwvEgGGsXN2E__DSIMF3iM")
# Directory for downloaded files
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Welcome message image URL
WELCOME_IMAGE_URL = "https://envs.sh/C_W.jpg"
CREATOR_URL = "https://t.me/zerocreations"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    
    # Download the welcome image
    async with aiohttp.ClientSession() as session:
        async with session.get(WELCOME_IMAGE_URL) as response:
            if response.status == 200:
                image_data = await response.read()
                
                # Create welcome message with keyboard
                keyboard = [
                    [InlineKeyboardButton("💬 Contact Creator", url=CREATOR_URL)],
                    [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_photo(
                    photo=image_data,
                    caption=f"Welcome to Zero Music Bot, {user.first_name}! 🎵\n\n"
                            f"Send me a YouTube link or search for a song, and I'll download it for you with high quality audio.",
                    reply_markup=reply_markup
                )
            else:
                # Fallback if image can't be loaded
                await update.message.reply_text(
                    f"Welcome to Zero Music Bot, {user.first_name}! 🎵\n\n"
                    f"Send me a YouTube link or search for a song, and I'll download it for you with high quality audio."
                )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    help_text = (
        "🎵 *Zero Music Bot Help* 🎵\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/search [query] - Search for music\n\n"
        "*How to use:*\n"
        "1️⃣ Send a YouTube link to download directly\n"
        "2️⃣ Or type /search followed by song name\n"
        "3️⃣ Select quality options when prompted\n\n"
        "Created by @zerocreations"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        help_text = (
            "🎵 *Zero Music Bot Help* 🎵\n\n"
            "*Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/search [query] - Search for music\n\n"
            "*How to use:*\n"
            "1️⃣ Send a YouTube link to download directly\n"
            "2️⃣ Or type /search followed by song name\n"
            "3️⃣ Select quality options when prompted\n\n"
            "Created by @zerocreations"
        )
        await query.edit_message_caption(caption=help_text, parse_mode="Markdown")
    elif query.data.startswith("download:"):
        # Extract video ID and quality
        parts = query.data.split(":")
        video_id = parts[1]
        quality = parts[2]
        
        # Inform user download is starting
        await query.edit_message_text(f"⏳ Starting download of video {video_id} in {quality} quality...\nPlease wait, this may take a moment.")
        
        # Handle download
        await download_music(update, context, video_id, quality)

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command."""
    if not context.args:
        await update.message.reply_text("Please provide a search term. Example: /search Bohemian Rhapsody")
        return
        
    search_query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Searching for: {search_query}")
    
    # Search for videos
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch5:{search_query}", download=False)['entries']
            
            if not search_results:
                await update.message.reply_text("No results found. Try a different search term.")
                return
                
            # Create keyboard with search results
            keyboard = []
            for result in search_results:
                video_id = result['id']
                title = result['title']
                duration = result.get('duration')
                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
                
                # Truncate title if too long
                if len(title) > 35:
                    title = title[:32] + "..."
                    
                keyboard.append([
                    InlineKeyboardButton(
                        f"{title} ({duration_str})",
                        callback_data=f"video:{video_id}"
                    )
                ])
                
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎵 Select a song to download:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await update.message.reply_text(f"Error searching: {str(e)}")

async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle YouTube links sent by the user."""
    youtube_url = update.message.text
    
    # Check if message contains a valid YouTube URL
    if not ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
        await update.message.reply_text("Please send a valid YouTube link or use /search to find music.")
        return
        
    await update.message.reply_text("⏳ Processing your YouTube link...")
    
    # Get video info
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
        try:
            info = ydl.extract_info(youtube_url, download=False)
            video_id = info['id']
            title = info['title']
            
            # Create quality selection keyboard
            keyboard = [
                [InlineKeyboardButton("🎵 MP3 (128kbps)", callback_data=f"download:{video_id}:128k")],
                [InlineKeyboardButton("🎵 MP3 (256kbps)", callback_data=f"download:{video_id}:256k")],
                [InlineKeyboardButton("🎵 MP3 (320kbps)", callback_data=f"download:{video_id}:320k")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send thumbnail and quality options
            if 'thumbnail' in info:
                async with aiohttp.ClientSession() as session:
                    async with session.get(info['thumbnail']) as response:
                        if response.status == 200:
                            thumb_data = await response.read()
                            await update.message.reply_photo(
                                photo=thumb_data,
                                caption=f"🎵 *{title}*\n\nSelect audio quality to download:",
                                reply_markup=reply_markup,
                                parse_mode="Markdown"
                            )
                            return
            
            # Fallback if thumbnail not available
            await update.message.reply_text(
                f"🎵 *{title}*\n\nSelect audio quality to download:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error processing YouTube link: {e}")
            await update.message.reply_text(f"Error processing the YouTube link: {str(e)}")

async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE, video_id: str, quality: str) -> None:
    """Download music from YouTube based on video ID and selected quality."""
    query = update.callback_query
    
    # Set quality parameters based on user selection
    bitrate = quality.replace('k', '')
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOADS_DIR}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': bitrate,
        }],
        'writethumbnail': True,
        'quiet': True,
    }
    
    status_message = await query.edit_message_text("⏬ Downloading... Please wait...")
    
    try:
        # Download using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            title = info['title']
            file_path = f"{DOWNLOADS_DIR}/{title}.mp3"
            
            # Ensure the downloaded file exists
            if not os.path.exists(file_path):
                for file in os.listdir(DOWNLOADS_DIR):
                    if file.endswith('.mp3'):
                        file_path = os.path.join(DOWNLOADS_DIR, file)
                        break
            
            # Try to find thumbnail
            thumbnail_path = None
            for file in os.listdir(DOWNLOADS_DIR):
                if file.endswith(('.jpg', '.png', '.webp')) and title in file:
                    thumbnail_path = os.path.join(DOWNLOADS_DIR, file)
                    break
            
            # Add metadata including thumbnail
            if os.path.exists(file_path):
                try:
                    audiofile = eyed3.load(file_path)
                    if audiofile is None:
                        audiofile = eyed3.core.AudioFile(file_path)
                    
                    if audiofile.tag is None:
                        audiofile.initTag()
                    
                    audiofile.tag.title = info.get('title', '')
                    audiofile.tag.artist = info.get('uploader', 'YouTube')
                    
                    # Add thumbnail if available
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        # Convert thumbnail to appropriate format if needed
                        with open(thumbnail_path, 'rb') as img_file:
                            audiofile.tag.images.set(3, img_file.read(), 'image/jpeg', 'Cover')
                    
                    audiofile.tag.save()
                except Exception as e:
                    logger.error(f"Error adding metadata: {e}")
            
            # Send the downloaded file
            await status_message.edit_text("✅ Download complete! Sending file...")
            
            # Send as audio file with proper caption
            if os.path.exists(file_path):
                with open(file_path, 'rb') as audio:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio,
                        title=info.get('title', ''),
                        performer=info.get('uploader', 'YouTube'),
                        caption=f"🎵 *{info.get('title', '')}*\n"
                               f"💾 Quality: {quality}\n"
                               f"🔗 [YouTube Link](https://www.youtube.com/watch?v={video_id})\n\n"
                               f"Downloaded by @ZeroMusicBot",
                        parse_mode="Markdown"
                    )
                
                # Clean up files
                if os.path.exists(file_path):
                    os.remove(file_path)
                if thumbnail_path and os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                
                await status_message.delete()
            else:
                await status_message.edit_text("❌ Error: Downloaded file not found.")
                
    except Exception as e:
        logger.error(f"Download error: {e}")
        await status_message.edit_text(f"❌ Download failed: {str(e)}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_music))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
