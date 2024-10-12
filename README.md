# Telegram Crypto Price Bot - Installation Guide

Welcome to the installation guide for the **BTCS Crypto Price Bot**! This bot allows you to fetch real-time market data for BTCS (Bitcoin Silver) from exchanges such as **Exbitron** and **Bitstorage**, view block explorer data, and check market cap and other useful information.

## Requirements

### 1. System Requirements
- **Python 3.8+**: The bot uses asynchronous functions, requiring at least Python 3.8.
- **Telegram Bot Token**: You'll need a bot token, which you can get from Telegram's [BotFather](https://core.telegram.org/bots#botfather).

### 2. Necessary Python Packages
You'll need several Python libraries to get the bot up and running, which will be installed automatically.

### 3. Virtual Environment (optional)
To keep your dependencies isolated, it's recommended to use a virtual environment.

---

## Installation Steps

### Step 1: Clone the Repository
First, clone this repository to your local machine. Open a terminal and run:
```bash
git clone https://github.com/RichtigerRaul/btcs_tgbot.git
```

### Step 2: Set Up Virtual Environment (optional but recommended)
To ensure package isolation, create a virtual environment:

For Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

Some key libraries include:
- `python-telegram-bot`: To interact with the Telegram API.
- `aiohttp`: For asynchronous HTTP requests.
- `python-dotenv`: To handle environment variables securely.

### Step 4: Set Up `.env` File for API Keys
To keep your sensitive data secure (like the Telegram and Exbitron API tokens), we will store them in a `.env` file. In the root directory of your project, create a `.env` file and add the following:

```env
TELEGRAM_API=your-telegram-bot-token
EXBITRON_API=your-exbitron-api-token
CHAT_ID=your-telegram-chat-id
```

Replace the values with your actual API keys and chat ID. Here’s an example using sample keys:

```env
TELEGRAM_API=84412934024:AAEkRhzprmSy1A0VUcXmKIsCisdfsdfaLE
EXBITRON_API=eyJhbGc384u9ofNiJ9.eyJleHAiOjE3Mjk3OTY0NTAsInN1YiI6InNlsdfsdpb24iLCJ...
CHAT_ID=-1032934832
```

In the Python code, you can load these environment variables using the `python-dotenv` library like this:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_API = os.getenv('TELEGRAM_API')
EXBITRON_API = os.getenv('EXBITRON_API')
CHAT_ID = os.getenv('CHAT_ID')
```

> **Note**: Never commit your `.env` file to a public repository. Add `.env` to your `.gitignore` to prevent it from being included in your commits.

### Step 5: Run the Bot
Once everything is set up, run the bot using the following command:
```bash
python bot_script.py
```

If the bot starts successfully, you'll see a message like **"Bot is starting..."** in the console. You can now interact with your bot on Telegram by sending commands such as `/start`, `/help`, or `/price`.

---

## Available Commands

The bot supports the following commands:

- **/start**: Initializes the bot and displays the main menu.
- **/price**: Fetches the current BTCS/USDT prices.
- **/help**: Lists all available commands.

---

## Bot Features

- **Market Data**: Get the latest BTCS/USDT prices, 24-hour high/low, and volume.
- **Exchange Switch**: Switch between Exbitron and Bitstorage exchanges.
- **Block Explorer**: Access data like network statistics, rich list, and recent transactions.
- **Support**: Contains a link to a support Telegram group.

---

## Troubleshooting

If you run into any issues, ensure:
- **Python version**: You are using Python 3.8 or later.
- **Installed packages**: All dependencies are installed correctly.
- **Correct API keys**: Double-check that you're using the correct API tokens.

---

## Contributing

Feel free to contribute by adding new features or improving the existing ones. The code is structured to be easy to understand and extend.

---

## Contact & Support

If you have any questions or need help setting up the bot, reach out to us in our [Support Telegram Chat](https://t.me/BTCSBITCOINSILVER).

---

**Enjoy using the bot!** 😊
