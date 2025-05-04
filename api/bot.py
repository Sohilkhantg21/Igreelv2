from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

BOT_TOKEN = "7544666074:AAEw39GCZKvvSgR8GmtCJdcYoWteCea54PI"
CHANNEL_USERNAME = "@SohilScriptee"
ADMIN_ID = "6411315434"  # Replace with your Telegram user ID
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
USERS_FILE = "users.json"

# Load users
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = []

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def send_message(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", data={"chat_id": chat_id, "text": text})

def send_video(chat_id, url):
    requests.post(f"{API_URL}/sendVideo", data={"chat_id": chat_id, "video": url})

def is_joined(user_id):
    res = requests.get(f"{API_URL}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}").json()
    status = res.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

@app.route("/api", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")
    username = message.get("from", {}).get("username", "unknown")

    # Register user
    if chat_id not in users:
        users.append(chat_id)
        save_users()
        send_message(ADMIN_ID, f"New user: @{username} ({chat_id})")

    # Check if user joined channel
    if not is_joined(chat_id):
        send_message(chat_id, f"Please join {CHANNEL_USERNAME} to use this bot.")
        return {"ok": True}

    # Reel downloader
    if "instagram.com/reel" in text:
        try:
            send_message(chat_id, "Downloading your reel...")
            res = requests.post("https://igram.world/api/ig", data={"link": text})
            video_url = res.json()["links"][0]["url"]
            send_video(chat_id, video_url)
        except:
            send_message(chat_id, "Failed to fetch reel. Please check the link.")
    else:
        send_message(chat_id, "Send a valid Instagram reel link.")
    return {"ok": True}
