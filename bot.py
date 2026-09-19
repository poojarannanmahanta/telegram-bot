import os
import asyncio
import logging

from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 10000))
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"]

# Flask
app = Flask(__name__)

# Telegram application
telegram_app = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋\n\n"
        "Your bot is working successfully! 🤖\n\n"
        "Try sending me a message."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show help"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text(
            f"You said:\n{update.message.text}"
        )


# Handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        echo
    )
)


@app.get("/")
def home():
    return "Telegram bot is running! 🤖"


@app.post("/webhook")
async def webhook():
    try:
        data = request.get_json()

        update = Update.de_json(
            data,
            telegram_app.bot
        )

        await telegram_app.update_queue.put(update)

        return "OK", 200

    except Exception:
        logger.exception("Error processing webhook")
        return "Error", 500


async def setup_bot():
    await telegram_app.initialize()

    await telegram_app.start()

    webhook_url = f"{RENDER_URL}/webhook"

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
    )

    logger.info("Webhook set to: %s", webhook_url)


async def main():
    await setup_bot()

    # Keep the process alive
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
