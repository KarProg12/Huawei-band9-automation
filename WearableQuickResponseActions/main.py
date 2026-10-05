import subprocess, json, time
from datetime import datetime

PHONE_NUM = "123456789"  # !ENTER YOUR PHONE NUMBER!

# Reminder settings
REMINDER_INTERVAL = 3  # Seconds to wait before checking if we need to resend
CHECK_INTERVAL = 3      # Seconds between each notification check


# ==========================================
# 🛠️ COMMAND DEFINITIONS SECTION (EXTEND HERE)
# ==========================================

def cmd_start():
    print("🚀 [ACTION] Launching main program procedure...")
    # Enter the code you want to execute when 'start' or 'y' is received here
    # Return True if you want to exit the main loop after this command, otherwise False
    return False 

def cmd_stop():
    print("🛑 [ACTION] Stopping background processes...")
    return False

def cmd_dnd_on():
    print("🔕 [ACTION] 'Do Not Disturb' mode turned ON.")
    return False

def cmd_dnd_off():
    print("🔔 [ACTION] 'Do Not Disturb' mode turned OFF.")
    return False

def cmd_exit():
    print("👋 [ACTION] Shutting down the script completely.")
    return True # Returning True breaks the main loop and exits the program


# 🗺️ COMMAND MAPPING DICTIONARY (ADD NEW COMMANDS HERE)
# Key: SMS text (always lowercase) -> Value: function name to execute
COMMANDS_MAP = {
    "start": cmd_start,
    "y": cmd_start,
    "yes": cmd_start,
    
    "stop": cmd_stop,
    "n": cmd_stop,
    "no": cmd_stop,
    
    "do not disturb on": cmd_dnd_on,
    "dnd on": cmd_dnd_on,
    
    "do not disturb off": cmd_dnd_off,
    "dnd off": cmd_dnd_off,
    
    "exit": cmd_exit,
    "quit": cmd_exit
}

# ==========================================
# ⚙️ TERMUX AND NOTIFICATION LOGIC
# ==========================================

def send_sms(content):
    print(f"💬 Sending SMS: '{content}'")
    sms_send_cmd = ["termux-sms-send", "-n", PHONE_NUM, content]
    try:
        subprocess.run(sms_send_cmd, check=True)
    except Exception as exception:
        print(f"Error while sending SMS: {exception}")

def remove_notification(notification_id):
    if not notification_id:
        return
    remove_cmd = ["termux-notification-remove", str(notification_id)]
    try:
        subprocess.run(remove_cmd, check=True)
        print(f"🧹 Removed processed notification ID: {notification_id}")
    except Exception as exception:
        print(f"Error while removing notification: {exception}")

def is_menu_notification_present():
    cmd = ["termux-notification-list"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        notifications = json.loads(result.stdout)
        for notification in notifications:
            if 'content' in notification:
                text = notification['content'].lower()
                if "available commands" in text:  # Matched to the new menu text
                    return True
    except Exception as exception:
        print(f"Error checking existing notifications: {exception}")
    return False

def process_incoming_notifications(start_time):
    """Checks notifications and runs the mapped function if a command is found."""
    cmd = ["termux-notification-list"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        notifications = json.loads(result.stdout)
        
        for notification in notifications:
            if 'content' in notification:
                text = notification['content'].strip()
                
                # Ignore our own menu messages
                if "available commands" in text.lower():
                    continue
                
                # Filter out old notifications
                if 'when' in notification and notification['when']:
                    try:
                        notif_time_object = datetime.strptime(notification['when'].strip(), "%Y-%m-%d %H:%M:%S")
                        if notif_time_object < start_time:
                            continue
                    except Exception:
                        pass
                
                clean_text = text.lower().strip()
                notification_id = notification.get('id')
                
                # 🚀 DYNAMIC COMMAND CHECK IN DICTIONARY
                if clean_text in COMMANDS_MAP:
                    remove_notification(notification_id)
                    # Fetch the function mapped to the text and execute it
                    action_function = COMMANDS_MAP[clean_text]
                    should_break_loop = action_function() 
                    return should_break_loop
                    
    except Exception as exception:
        print(f"Notification reading error: {exception}")
    return False

# ==========================================
# 🔄 MAIN PROGRAM LOOP
# ==========================================

script_start_time = datetime.now()

# Sending the initial menu list
MENU_TEXT = "Available commands: start, stop, dnd on, dnd off, exit"
send_sms(MENU_TEXT)
last_sms_sent_time = time.time()

print("\n📡 System ready. Waiting for commands from your smart band...")

while True:
    time.sleep(CHECK_INTERVAL)
    
    # Process notifications. If a command function returns True, break the loop.
    if process_incoming_notifications(script_start_time):
        break
        
    # Reminder and Anti-Spam logic
    if time.time() - last_sms_sent_time > REMINDER_INTERVAL:
        if is_menu_notification_present():
            print("  [Anti-Spam] Menu is still visible on the phone. Skipping SMS resend.")
            last_sms_sent_time = time.time() 
        else:
            print("\n⏳ No active menu on the screen. Sending reminder...")
            send_sms(MENU_TEXT)
            last_sms_sent_time = time.time()

print("\n🏁 Program control loop has terminated.")

