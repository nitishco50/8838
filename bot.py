from flask import Flask, request, send_file, jsonify
import os
import base64
import threading
import telebot
from telebot import types
import yt_dlp
import uuid

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)

# Secured links
YOUTUBE_B64 = "aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE="
SUPPORT_B64 = "aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA="
YOUTUBE_URL = base64.b64decode(YOUTUBE_B64).decode("utf-8")
SUPPORT_URL = base64.b64decode(SUPPORT_B64).decode("utf-8")

app = Flask(__name__)

# ==================== KEEP ALIVE + API ====================
@app.route("/")
def home():
    return "BLACK_KNOWLEDGE_190 Video Downloader Bot is Alive ✅"

# ========== NEW: Website API Endpoint ==========
@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        data = request.get_json(silent=True) or request.form
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"status": "error", "message": "URL is required"}), 400

        if not any(x in url for x in ["instagram.com", "facebook.com", "fb.watch", "fb.com"]):
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
            return jsonify({"status": "error", "message": "Download failed. Link may be private."}), 400

        # Send file and delete after sending
        return send_file(
            filename,
            as_attachment=True,
            download_name=f"BLACK_KNOWLEDGE_190_{int(time.time())}.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)[:200]}), 500
    finally:
        # Cleanup (extra safety)
        try:
            if "filename" in locals() and os.path.exists(filename):
                os.remove(filename)
        except:
            pass

def run_flask():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==================== TELEGRAM BOT PART (same as before) ====================
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 SUBSCRIBE CHANNEL", url=YOUTUBE_URL),
        types.InlineKeyboardButton("📚 ALL TUTORIALS", url=YOUTUBE_URL),
        types.InlineKeyboardButton("💬 CONTACT OWNER", url=SUPPORT_URL)
    )
    welcome_text = (
        "╔══════════════════════════════════╗\n"
        "║     🔥  BLACK KNOWLEDGE 190  🔥     ║\n"
        "╚══════════════════════════════════╝\n\n"
        "Welcome to the *Premium Video Downloader Bot*!\n\n"
        "📥 Supported Platforms:\n"
        "• Instagram Reels\n"
        "• Facebook Videos\n\n"
        "Simply send any Instagram Reel or Facebook video link.\n\n"
        "⚡ Fast • Secure • Clean\n"
        "Powered by @BLACK_KNOWLEDGE_190"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    # (Your previous download logic remains exactly same)
    # ... keep the previous handle_link function here ...
    pass   # ← yahan apna purana handle_link code paste kar dena

# ==================== MAIN ====================
if __name__ == "__main__":
    import time
    keep_alive()
    print("Bot + API started | @BLACK_KNOWLEDGE_190")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
