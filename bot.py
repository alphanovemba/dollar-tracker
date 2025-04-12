import os
import json
import datetime
import base64
import requests
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
)

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # e.g. username/repo-name
FILE_PATH = "rates.json"
BRANCH = "main"
BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "").split(",")  # comma-separated user IDs

# GitHub helper functions
def fetch_github_file():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None, f"Error fetching file: {res.text}"
    data = res.json()
    content = json.loads(requests.get(data["download_url"]).text)
    return {"sha": data["sha"], "content": content}, None

def push_github_file(updated_content, sha, message):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    encoded_content = base64.b64encode(json.dumps(updated_content, indent=2).encode("utf-8")).decode()
    payload = {
        "message": message,
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }
    res = requests.put(url, headers=headers, json=payload)
    return res.status_code == 200, res.text

# Command: /setrate
async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to set the rate.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setrate <rate>")
        return

    try:
        new_rate = float(context.args[0])
        today = datetime.date.today().isoformat()
        data, error = fetch_github_file()
        if error:
            await update.message.reply_text(error)
            return
        data["content"].append({"date": today, "rate": new_rate})
        success, result = push_github_file(data["content"], data["sha"], f"Update rate for {today}")
        if success:
            await update.message.reply_text(f"✅ Updated rate to {new_rate} for {today}")
        else:
            await update.message.reply_text(f"❌ GitHub error: {result}")
    except ValueError:
        await update.message.reply_text("Invalid rate. Please enter a number.")

# Command: /deleterate
async def deleterate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to delete rates.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /deleterate <YYYY-MM-DD>")
        return

    target_date = context.args[0]
    data, error = fetch_github_file()
    if error:
        await update.message.reply_text(error)
        return

    original_length = len(data["content"])
    data["content"] = [entry for entry in data["content"] if entry["date"] != target_date]

    if len(data["content"]) == original_length:
        await update.message.reply_text(f"No entry found for {target_date}.")
        return

    success, result = push_github_file(data["content"], data["sha"], f"Delete rate for {target_date}")
    if success:
        await update.message.reply_text(f"✅ Deleted rate for {target_date}")
    else:
        await update.message.reply_text(f"❌ GitHub error: {result}")

# Inline query support
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    data, error = fetch_github_file()
    if error or not data["content"]:
        results = [InlineQueryResultArticle(
            id="1",
            title="No data available",
            input_message_content=InputTextMessageContent("No exchange rate data yet.")
        )]
    else:
        latest = data["content"][-1]
        msg = f"💵 USD Rate (MV): MVR {latest['rate']} ({latest['date']})"
        results = [InlineQueryResultArticle(
            id="1",
            title="Show current USD rate",
            input_message_content=InputTextMessageContent(msg)
        )]

    await update.inline_query.answer(results, cache_time=5)

# Start the bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("setrate", setrate))
    app.add_handler(CommandHandler("deleterate", deleterate))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()
