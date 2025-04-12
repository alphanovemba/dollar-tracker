import os
import json
import datetime
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # e.g. username/repo-name
FILE_PATH = "rates.json"
BRANCH = "main"

async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setrate <rate>")
        return
    new_rate = float(context.args[0])
    today = datetime.date.today().isoformat()

    # Get current file from GitHub
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    response = requests.get(url, headers=headers).json()

    content = json.loads(
        requests.get(response["download_url"]).text
    )
    content.append({"date": today, "rate": new_rate})

    updated_content = json.dumps(content, indent=2)
    encoded = updated_content.encode("utf-8").decode("latin1")

    commit_msg = f"Update rate for {today}"
    put_data = {
        "message": commit_msg,
        "content": encoded.encode("utf-8").decode("utf-8").encode("base64").decode(),
        "sha": response["sha"]
    }
    requests.put(url, headers=headers, json=put_data)
    await update.message.reply_text(f"Updated rate to {new_rate} for {today}")

if __name__ == '__main__':
    from telegram.ext import CommandHandler
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("setrate", setrate))
    app.run_polling()