import os
import base64
import threading
import time
import uuid
from flask import Flask, request, send_file, jsonify
import telebot
from telebot import types
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

YOUTUBE_B64 = "aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE="
SUPPORT_B64 = "aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA="
YOUTUBE_URL = base64.b64decode(YOUTUBE_B64).decode("utf-8")
SUPPORT_URL = base64.b64decode(SUPPORT_B64).decode("utf-8")

app = Flask(__name__)

@app.route("/")
def home():
    return "BLACK_KNOWLEDGE_190 Video Downloader Bot is Alive ✅"

@app.route("/api/download", methods=["POST", "OPTIONS"])
def api_download():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    try:
        data = request.get_json(silent=True) or request.form
        url = (data.get("url") or "").strip()

        if not url:
            return jsonify({"status": "error", "message": "URL is required"}), 400

        if not any(x in url.lower() for x in ["instagram.com", "facebook.com", "fb.watch", "fb.com"]):
            return jsonify({"status": "error", "message": "Only Instagram Reels & Facebook Videos supported"}), 400

        filename = f"temp_{uuid.uuid4().hex}.mp4"

        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(filename) or os.path.getsize(filename) < 10000:
            if os.path.exists(filename):
                os.remove(filename)
            return jsonify({"status": "error", "message": "Download failed. Link private or unsupported."}), 400

        response = send_file(
            filename,
            as_attachment=True,
            download_name=f"BLACK_KNOWLEDGE_190_{int(time.time())}.mp4",
            mimetype="video/mp4"
        )
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)[:250]}), 500
    finally:
        try:
            if "filename" in locals() and os.path.exists(filename):
                os.remove(filename)
        except:
            pass

@bot.message_handler(commands=["start", "help"])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 SUBSCRIBE CHANNEL", url=YOUTUBE_URL),
        types.InlineKeyboardButton("📚 ALL TUTORIALS", url=YOUTUBE_URL),
        types.InlineKeyboardButton("💬 CONTACT OWNER", url=SUPPORT_URL)
    )

    text = """
╔══════════════════════════════════╗
║     🔥  BLACK KNOWLEDGE 190  🔥     ║
╚══════════════════════════════════╝

Welcome to the <b>Premium Video Downloader Bot</b>!

📥 Supported Platforms:
• Instagram Reels
• Facebook Videos

Simply send any Instagram Reel or Facebook video link.

⚡ Fast • Secure • Clean
Powered by @BLACK_KNOWLEDGE_190
"""
    bot.send_message(message.chat.id, text, reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_link(message):
    url = message.text.strip()

    if not any(x in url.lower() for x in ["instagram.com", "facebook.com", "fb.watch", "fb.com"]):
        bot.reply_to(message, "❌ Please send a valid Instagram Reel or Facebook Video link.")
        return

    status = bot.reply_to(message, "🔍 Analyzing...")

    try:
        bot.edit_message_text("⬇️ Downloading (50%)...", chat_id=message.chat.id, message_id=status.message_id)

        filename = f"temp_{uuid.uuid4().hex}.mp4"
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": filename,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(filename) or os.path.getsize(filename) < 10000:
            raise Exception("File download failed or too small")

        bot.edit_message_text("📤 Uploading (100%)...", chat_id=message.chat.id, message_id=status.message_id)

        with open(filename, "rb") as video:
            bot.send_video(
                message.chat.id,
                video,
                caption="Downloaded Successfully! Power by: @BLACK_KNOWLEDGE_190",
                supports_streaming=True,
                reply_to_message_id=message.message_id
            )

        bot.delete_message(message.chat.id, status.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)[:180]}", chat_id=message.chat.id, message_id=status.message_id)
    finally:
        try:
            if "filename" in locals() and os.path.exists(filename):
                os.remove(filename)
        except:
            pass

def run_bot():
    print("Telegram Bot started polling...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30, none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port)
