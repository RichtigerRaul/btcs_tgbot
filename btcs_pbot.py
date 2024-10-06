import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import logging
from datetime import datetime

# Configuration
EXBITRON_API_URL = "https://api.exbitron.digital/api/v2/peatio/public/markets/btcsusdt/tickers"
TELEGRAM_TOKEN = "YOUR TOKEN ID"
TOTAL_SUPPLY = 21000000  # Assumed total supply of BTCS Tokens
BOT_VERSION = "v2.2.0"
SUPPORT_GROUP_LINK = "https://t.me/BTCSBITCOINSILVER"
WEBSITE_LINK = "https://bitcoinsilver.top/"  # Replace with the actual website URL
BITSTORAGE_LINK = "https://bitstorage.finance/news/btcs-will-be-listed-on-bitstorage"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def get_market_data():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(EXBITRON_API_URL) as response:
                if response.status != 200:
                    logger.error(f"Exbitron API error: {response.status}")
                    return None
                data = await response.json()
                return data.get('ticker')
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

def format_price_message(ticker):
    last_price = float(ticker['last'])
    high_price = float(ticker['high'])
    low_price = float(ticker['low'])
    volume = float(ticker['volume'])
    price_change = ticker['price_change_percent']
    market_cap = last_price * TOTAL_SUPPLY

    price_emoji = "🚀" if float(price_change[:-1]) > 0 else "📉"

    return (
        f"{price_emoji} *BTCS/USDT Market Update* {price_emoji}\n\n"
        f"💰 Current Price: ${last_price:.8f}\n"
        f"📈 24h High: ${high_price:.8f}\n"
        f"📉 24h Low: ${low_price:.8f}\n"
        f"📊 24h Volume: {volume:.2f} BTCS\n"
        f"📊 Price Change: {price_change}\n"
        f"💼 Market Cap: ${market_cap:,.2f}\n\n"
        f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📊 BTCS Price", callback_data='btcs')],
        [InlineKeyboardButton("🌐 Website/Wallet", callback_data='website')],
        [InlineKeyboardButton("🔄 Exchanges", callback_data='exchanges')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help'),
         InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"🌟 Welcome to the BTCS Price Bot! 🌟\n"
        f"Version: {BOT_VERSION}\n\n"
        "Track BTCS prices, access our website/wallet, and check exchanges.\n"
        "Choose an option to get started:"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = f"""
🤖 *BTCS Bot Help* (Version: {BOT_VERSION})

Commands:
/start - Show the main menu 🏠
/btcs - Get current BTCS price and market info 💰
/help - Display this help message ℹ️

Features:
• Real-time BTCS price updates 📊
• Quick access to our website and wallet 🌐
• Information about exchanges where BTCS is listed 🔄
• Support group link 💬

How to use:
1. Click on '📊 BTCS Price' to get the latest market information
2. Use '🌐 Website/Wallet' to visit our website and access your wallet
3. Check '🔄 Exchanges' to see where you can trade BTCS
4. Join our support group if you need assistance

For any issues or questions, please use the Support button to join our support group.
    """
    keyboard = [[InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")

async def btcs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ticker = await get_market_data()
    if ticker:
        message = format_price_message(ticker)
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data='btcs')],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        error_message = "❌ Unable to fetch market data. Please try again later."
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.edit_text(error_message, parse_mode="Markdown")
        else:
            await update.message.reply_text(error_message, parse_mode="Markdown")

async def website_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🌐 *BTCS Website and Wallet* 🌐\n\n"
        "Visit our website to access your BTCS wallet and explore more features:\n\n"
        f"{WEBSITE_LINK}\n\n"
        "On our website, you can:\n"
        "• Access your BTCS wallet\n"
        "• View latest news and updates\n"
        "• Explore BTCS features and benefits"
    )
    keyboard = [[InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(message, reply_markup=reply_markup, parse_mode="Markdown")

async def exchanges_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exchanges_text = """
🔄 *BTCS Exchanges*

Choose an exchange to view BTCS trading information:
    """
    keyboard = [
        [InlineKeyboardButton("✅ Exbitron", callback_data='exbitron')],
        [InlineKeyboardButton("🔜 Bitstorage", callback_data='bitstorage')],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.edit_text(exchanges_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'btcs':
        await btcs_command(update, context)
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'start':
        await start(update, context)
    elif query.data == 'website':
        await website_command(update, context)
    elif query.data == 'exchanges':
        await exchanges_command(update, context)
    elif query.data == 'exbitron':
        await btcs_command(update, context)
    elif query.data == 'bitstorage':
        bitstorage_message = f"🔜 Coming soon!\n\n{BITSTORAGE_LINK}"
        keyboard = [[InlineKeyboardButton("🔙 Back to Exchanges", callback_data='exchanges')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(bitstorage_message, reply_markup=reply_markup, parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        # Send a message to the user
        error_message = "An error occurred while processing your request. Please try again later."
        if update.effective_message:
            await update.effective_message.reply_text(error_message)
    except:
        pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.startswith('/'):
        command = update.message.text.split()[0].lower()
        if command == '/start':
            await start(update, context)
        elif command == '/help':
            await help_command(update, context)
        elif command == '/btcs':
            await btcs_command(update, context)

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("btcs", btcs_command))
    
    # Add callback query handler for button presses
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Add message handler for text commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
