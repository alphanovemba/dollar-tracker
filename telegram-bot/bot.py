import os
import json
import datetime
import base64
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")  # e.g. username/repo-name
FILE_PATH = "../rates.json"
BRANCH = "main"

async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /setrate <rate>")
        return
    try:
        new_rate = float(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid rate value!")
        return

    today = datetime.date.today().isoformat()

    # Get current file from GitHub
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        await update.message.reply_text(f"Error fetching file from GitHub: {response.text}")
        return

    response_json = response.json()
    content = json.loads(requests.get(response_json["download_url"]).text)
    content.append({"date": today, "rate": new_rate})

    updated_content = json.dumps(content, indent=2)

    # Encode the content to base64
    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    commit_msg = f"Update rate for {today}"
    put_data = {
        "message": commit_msg,
        "content": encoded_content,
        "sha": response_json["sha"]
    }

    # Send the PUT request to update the file on GitHub
    put_response = requests.put(url, headers=headers, json=put_data)

    if put_response.status_code == 200:
        await update.message.reply_text(f"Updated rate to {new_rate} for {today}")
    else:
        await update.message.reply_text(f"Failed to update GitHub: {put_response.text}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    app.add_handler(CommandHandler("setrate", setrate))
    app.run_polling()
