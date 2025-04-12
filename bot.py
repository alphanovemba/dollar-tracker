import os
import json
import datetime
import requests
import base64
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load .env variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # e.g. username/dollar-tracker-mv
FILE_PATH = "rates.json"
BRANCH = "main"

# Telegram command to set today's rate
async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setrate <rate>")
        return

    try:
        new_rate = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid rate. Please enter a number.")
        return

    today = datetime.date.today().isoformat()

    # Get current file from GitHub
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await update.message.reply_text(f"Error fetching file from GitHub: {response.text}")
        return

    response_json = response.json()
    raw_data = requests.get(response_json["download_url"]).text.strip()

    if not raw_data:
        content = []
    else:
        try:
            content = json.loads(raw_data)
        except json.JSONDecodeError:
            await update.message.reply_text("⚠️ Couldn't parse existing rate data. Starting fresh.")
            content = []

    content.append({"date": today, "rate": new_rate})
    updated_content = json.dumps(content, indent=2)

    encoded = base64.b64encode(updated_content.encode()).decode()
    put_data = {
        "message": f"Update rate for {today}",
        "content": encoded,
        "sha": response_json["sha"],
        "branch": BRANCH
    }

    put_response = requests.put(url, headers=headers, json=put_data)

    if put_response.status_code in [200, 201]:
        await update.message.reply_text(f"✅ Updated rate to {new_rate} for {today}")
    else:
        await update.message.reply_text(f"❌ Failed to update rate: {put_response.text}")

# Start the bot
if __name__ == '__main__':
    print("🤖 Bot is starting up...")
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("setrate", setrate))
    app.run_polling()
