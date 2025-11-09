import os
import threading
from flask import Flask
import telebot

# --- Flask "keep-alive" server ---
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is alive', 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Start the web server in a background thread
threading.Thread(target=run_flask).start()

# --- Telegram bot ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = -5024743724   # replace with your admin group ID

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN)
user_map = {}

@bot.message_handler(commands=['msg'])
def handle_user_msg(message):
    if message.chat.type != "private":
        bot.reply_to(message, "❗ Please send me /msg in private chat.")
        return

    text = message.text.replace('/msg', '', 1).strip()
    if not text:
        bot.reply_to(message, "Usage: /msg your message here")
        return

    user = message.from_user
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else ""
    msg_text = f"📩 From {name} {username}\nUser ID: {user.id}\n\n{text}"

    sent = bot.send_message(ADMIN_GROUP_ID, msg_text)
    user_map[sent.message_id] = user.id
    bot.reply_to(message, "✅ Message sent to admins!")

@bot.message_handler(func=lambda m: m.reply_to_message and m.chat.id == ADMIN_GROUP_ID)
def handle_admin_reply(message):
    replied = message.reply_to_message
    if replied.message_id not in user_map:
        return
    user_id = user_map[replied.message_id]
    bot.send_message(user_id, f"👨‍💼 Admin: {message.text}")

while True:
    try:
        print("🔄 Starting bot polling...")
        bot.polling(none_stop=True)
    except Exception as e:
        print("⚠️ Polling error:", e)



