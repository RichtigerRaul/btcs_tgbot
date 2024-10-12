import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import logging
from datetime import datetime
import json

# Configuration
EXBITRON_API_URL = "https://api.exbitron.digital/api/v2/peatio/public/markets/btcsusdt/tickers"
BITSTORAGE_API_URL = "https://api.bitstorage.finance/v1/public/ticker"
BITSTORAGE_SYMBOLS_URL = "https://api.bitstorage.finance/v1/public/symbols"
BTCS_SUPPLY_API_URL = "http://explorer.btcs.pools4mining.com:3001/ext/getmoneysupply"
TELEGRAM_TOKEN = "(---------YOUR_TELEGRAM_TOKEN_HERE----------)"
MAX_SUPPLY = 21000000  # Maximum supply of BTCS
BOT_VERSION = "v4.2.0"
SUPPORT_GROUP_LINK = "https://t.me/BTCSBITCOINSILVER"
WEBSITE_LINK = "https://bitcoinsilver.top/"
BITSTORAGE_LINK = "https://bitstorage.finance/spot/trading/BTCSUSDT?interface=classic"
BLOCK_EXPLORER_LINK = "http://explorer.btcs.pools4mining.com:3001"

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global variable for the current exchange
current_exchange = "exbitron"

async def fetch_data(url, params=None, headers=None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=headers) as response:
                logger.info(f"API Response Status: {response.status}")
                logger.info(f"API Request URL: {response.url}")
                
                if response.status == 200:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        data = await response.json()
                    else:
                        data = await response.text()
                    logger.info(f"API Response: {data}")
                    return data
                else:
                    logger.error(f"API error: {response.status}, Response: {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

async def get_exbitron_data():
    data = await fetch_data(EXBITRON_API_URL)
    return data.get('ticker') if data else None

async def get_bitstorage_data():
    headers = {"User-Agent": "CryptoPriceBot/1.0"}
    symbols = await fetch_data(BITSTORAGE_SYMBOLS_URL) or []
    btcs_symbols = [symbol['pair'] for symbol in symbols.get('data', []) if symbol['pair'].startswith('BTCS')]
    
    if not btcs_symbols:
        btcs_symbols = ["BTCSUSDT", "BTCSUSD", "BTCSEUR"]
    
    for symbol in btcs_symbols:
        data = await fetch_data(BITSTORAGE_API_URL, params={"pair": symbol}, headers=headers)
        if data and data.get('status'):
            return data
    
    logger.error("Failed to fetch Bitstorage data for BTCS symbols")
    return None

async def get_circulating_supply():
    supply_data = await fetch_data(BTCS_SUPPLY_API_URL)
    if supply_data:
        try:
            return float(supply_data)
        except ValueError:
            logger.error(f"Invalid circulating supply data: {supply_data}")
    return None

def format_large_number(number):
    if number >= 1e9:
        return f"{number / 1e9:.2f}B"
    elif number >= 1e6:
        return f"{number / 1e6:.2f}M"
    elif number >= 1e3:
        return f"{number / 1e3:.2f}K"
    else:
        return f"{number:.2f}"

def format_message(data, exchange, circulating_supply):
    if not data:
        return f"❌ Error fetching {exchange} market data. Please try again later."

    if exchange == "exbitron":
        last_price = float(data['last'])
        high_price = float(data['high'])
        low_price = float(data['low'])
        volume = float(data['volume'])
        price_change = data['price_change_percent']
    else:  # bitstorage
        ticker_data = data['data']
        last_price = float(ticker_data.get('last', 0))
        high_price = float(ticker_data.get('high', 0))
        low_price = float(ticker_data.get('low', 0))
        volume = float(ticker_data.get('volume_24H', 0))
        open_price = float(ticker_data.get('open', 0))
        price_change = f"{((last_price - open_price) / open_price) * 100:.2f}%" if open_price != 0 else "N/A"

    market_cap = last_price * circulating_supply if circulating_supply else "N/A"
    price_emoji = "🚀" if price_change != "N/A" and float(price_change[:-1]) > 0 else "📉"

    return (
        f"{price_emoji} *BTCS/USDT Market Update\n ({exchange.capitalize()})* {price_emoji}\n\n"
        f"💰 Current Price: ${last_price:.8f}\n"
        f"📈 24h High: ${high_price:.8f}\n"
        f"📉 24h Low: ${low_price:.8f}\n"
        f"📊 24h Volume: {format_large_number(volume)} BTCS\n"
        f"📊 Price Change: {price_change}\n"
        f"💼 Market Cap: ${format_large_number(market_cap) if market_cap != 'N/A' else 'N/A'}\n"
        f"💱 Circulating Supply: {format_large_number(circulating_supply) if circulating_supply else 'N/A'} BTCS\n"
        f"📈 Max Supply: {format_large_number(MAX_SUPPLY)} BTCS\n\n"
        f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

def get_keyboard(include_back_button=True):
    keyboard = [
        [
            InlineKeyboardButton("✅ Exbitron" if current_exchange == 'exbitron' else "Exbitron", callback_data='select_exbitron'),
            InlineKeyboardButton("✅ Bitstorage" if current_exchange == 'bitstorage' else "Bitstorage", callback_data='select_bitstorage')
        ],
        [InlineKeyboardButton("🔍 Block Explorer Info", callback_data='block_explorer')],
        [InlineKeyboardButton("🌐 Website/Wallet", callback_data='website')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help'),
         InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP_LINK)]
    ]
    if include_back_button:
        keyboard.append([InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')])
    return InlineKeyboardMarkup(keyboard)

def get_block_explorer_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Network Stats", callback_data='network_stats')],
        [InlineKeyboardButton("💰 Rich List", callback_data='rich_list')],
        [InlineKeyboardButton("🔗 Latest Blocks", callback_data='latest_blocks')],
        [InlineKeyboardButton("💼 Latest Transactions", callback_data='latest_txs')],
        [InlineKeyboardButton("🏠 Explorer Home", url=BLOCK_EXPLORER_LINK)],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data='start')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        f"🌟 Welcome to the BTCS Price Bot! 🌟\n"
        f"Version: {BOT_VERSION} - Bot Creator:@Durakson\n\n"
        f"Current Exchange: {current_exchange.capitalize()}\n\n"
        "Track BTCS prices, access our website/wallet, and get Block Explorer info.\n"
        "Choose an option to get started:"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(welcome_text, reply_markup=get_keyboard(include_back_button=False), parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_keyboard(include_back_button=False), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = f"""
🤖 *BTCS Bot Help* (Version: {BOT_VERSION})

Commands:
/start - Show the main menu 🏠
/price - Get current BTCS price 💰
/help - Display this help message ℹ️

Features:
• Real-time BTCS price updates from Exbitron and Bitstorage 📊
• Live market cap and circulating supply information 💼
• Quick access to our website and wallet 🌐
• BTCS Block Explorer information 🔍
• Ability to switch between exchanges 🔄
• Support group link 💬

How to use:
1. Select your preferred exchange (Exbitron or Bitstorage)
2. Use the Block Explorer Info to learn about the BTCS network
3. Use 'Website/Wallet' to visit our website and access your wallet
4. Join our support group if you need assistance

For any issues or questions, please use the Support button to join our support group.
    """
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(help_text, reply_markup=get_keyboard(), parse_mode="Markdown")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await get_exbitron_data() if current_exchange == "exbitron" else await get_bitstorage_data()
    circulating_supply = await get_circulating_supply()
    message = format_message(data, current_exchange, circulating_supply)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(message, reply_markup=get_keyboard(), parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(message, reply_markup=get_keyboard(), parse_mode="Markdown")

async def switch_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE, new_exchange: str) -> None:
    global current_exchange
    current_exchange = new_exchange
    await price_command(update, context)

async def website_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🌐 *BTCS Website and Wallet* 🌐\n\n"
        "Visit our website to access your wallet and explore more features:\n\n"
        f"{WEBSITE_LINK}\n\n"
        "On our website, you can:\n"
        "• Access your BTCS wallet\n"
        "• View latest news and updates\n"
        "• Explore features and benefits of BTCS"
    )
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_keyboard(), parse_mode="Markdown")

async def block_explorer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🔍 *BTCS Block Explorer Information* 🔍\n\n"
        "Welcome to the Block Explorer section. Here you can access detailed information about the BTCS network.\n\n"
        f"Choose an option to explore:"
    )
    
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_block_explorer_keyboard(), parse_mode="Markdown")

async def network_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    basic_stats = await fetch_data(f"{BLOCK_EXPLORER_LINK}/ext/getbasicstats")
    summary = await fetch_data(f"{BLOCK_EXPLORER_LINK}/ext/getsummary")
    
    if basic_stats and summary:
        message = (
            "📊 *BTCS Network Statistics* 📊\n\n"
            f"🔢 Block Count: {basic_stats['block_count']}\n"
            f"💰 Circulating Supply: {format_large_number(float(basic_stats['money_supply']))} BTCS\n"
            f"💲 USDT Price: ${float(basic_stats['last_price_usdt']):.8f}\n"
            f"💵 USD Price: ${float(basic_stats['last_price_usd']):.8f}\n"
            f"🔨 Difficulty: {float(summary['difficulty']):.2f}\n"
            f"⚡ Network Hashrate: {summary['hashrate']}\n"
            f"🔌 Connections: {summary['connections']}\n\n"
            f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        message = "❌ Error fetching network statistics. Please try again later."
    
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_block_explorer_keyboard(), parse_mode="Markdown")

async def rich_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    distribution = await fetch_data(f"{BLOCK_EXPLORER_LINK}/ext/getdistribution")
    
    if distribution:
        message = "💰 *BTCS Rich List* 💰\n\n"
        for key, item in distribution.items():
            if key != 'supply':
                message += f"• {item['percent']}% of addresses hold {item['total']} BTCS\n"
        message += f"\n🔗 [View Full Rich List]({BLOCK_EXPLORER_LINK}/richlist)\n"
    else:
        message = "❌ Error fetching rich list data. Please try again later."
    
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_block_explorer_keyboard(), parse_mode="Markdown")

async def latest_blocks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🔗 *Latest BTCS Blocks* 🔗\n\n"
        "The API method to retrieve the latest blocks is currently disabled.\n\n"
        "To view the most recent blocks, please visit the BTCS Explorer directly:\n"
        f"[BTCS Explorer]({BLOCK_EXPLORER_LINK})\n\n"
        "There you can find information about:\n"
        "• Recent blocks and their details\n"
        "• Transaction history\n"
        "• Network statistics\n"
        "• And more!\n\n"
        "We apologize for the inconvenience and thank you for your understanding."
    )
    
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_block_explorer_keyboard(), parse_mode="Markdown", disable_web_page_preview=True)

async def latest_txs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txs = await fetch_data(f"{BLOCK_EXPLORER_LINK}/ext/getlasttxs/0/10")
    
    if txs:
        message = "💼 *Latest BTCS Transactions* 💼\n\n"
        for tx in txs[:5]:  # Show last 5 transactions
            amount = float(tx['amount'])
            message += f"• {tx['txid'][:8]}...{tx['txid'][-8:]}: {amount:.8f} BTCS\n"
        message += f"\n🔗 [View All Transactions]({BLOCK_EXPLORER_LINK})\n"
    else:
        message = "❌ Error fetching latest transactions. Please try again later."
    
    await update.callback_query.answer()
    await update.callback_query.message.edit_text(message, reply_markup=get_block_explorer_keyboard(), parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'price':
        await price_command(update, context)
    elif query.data == 'select_exbitron':
        await switch_exchange(update, context, 'exbitron')
    elif query.data == 'select_bitstorage':
        await switch_exchange(update, context, 'bitstorage')
    elif query.data == 'help':
        await help_command(update, context)
    elif query.data == 'start':
        await start(update, context)
    elif query.data == 'website':
        await website_command(update, context)
    elif query.data == 'block_explorer':
        await block_explorer_command(update, context)
    elif query.data == 'network_stats':
        await network_stats(update, context)
    elif query.data == 'rich_list':
        await rich_list(update, context)
    elif query.data == 'latest_blocks':
        await latest_blocks(update, context)
    elif query.data == 'latest_txs':
        await latest_txs(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        error_message = "An error occurred while processing your request. Please try again later."
        if update.effective_message:
            await update.effective_message.reply_text(error_message)
    except:
        pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        command = update.message.text.split()[0].lower()
        if command == '/start':
            await start(update, context)
        elif command == '/help':
            await help_command(update, context)
        elif command == '/price':
            await price_command(update, context)

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
