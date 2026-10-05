import subprocess, json, time
from datetime import datetime

PHONE_NUM = "123456789" # !ENTER YOUR PHONE NUMBER!

# Reminder settings
REMINDER_INTERVAL = 30  # Seconds to wait before checking if we need to resend
CHECK_INTERVAL = 3      # Seconds between each notification check

def send_sms_question(content):
    print(f"💬 Sending SMS to huawei band 9:\n'{content}'")
    sms_send_cmd = ["termux-sms-send", "-n", PHONE_NUM, content]
    try:
        subprocess.run(sms_send_cmd, check=True)
    except Exception as exception:
        print(f"Error while sending SMS: {exception}")

def remove_notification(notification_id):
    """Dismisses a notification so it won't be read again next time."""
    if not notification_id:
        return
    remove_cmd = ["termux-notification-remove", str(notification_id)]
    try:
        subprocess.run(remove_cmd, check=True)
        print(f"🧹 Removed processed notification ID: {notification_id}")
    except Exception as exception:
        print(f"Error while removing notification: {exception}")

def is_question_notification_present():
    """Checks if the question SMS notification is still active on the device."""
    cmd = ["termux-notification-list"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        notifications = json.loads(result.stdout)
        for notification in notifications:
            if 'content' in notification:
                text = notification['content'].lower()
                # Check if our specific question is still visible in notifications
                if "do you want to start" in text:
                    return True
    except Exception as exception:
        print(f"Error checking existing notifications: {exception}")
    return False

def check_answer_for_notification(start_time):
    cmd = ["termux-notification-list"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        notifications = json.loads(result.stdout)
        
        for notification in notifications:
            if 'content' in notification:
                text = notification['content'].strip()
                
                # BYPASSING OWN QUESTION
                if "do you want to start" in text.lower():
                    continue
                
                # FILTERING OLD NOTIFICATIONS (Aligned timezone with datetime objects)
                if 'when' in notification and notification['when']:
                    try:
                        # Process the text format to local time object
                        notif_time_object = datetime.strptime(notification['when'].strip(), "%Y-%m-%d %H:%M:%S")
                        
                        # If notification existed before start of script ignore it
                        if notif_time_object < start_time:
                            continue
                    except Exception:
                        # If the time format was different in other notifications go further
                        pass
                
                # STRICT TEXT CLEANING
                clean_text = text.lower().strip()
                notification_id = notification.get('id')
                
                # EXACT MATCHING: Check for definitive responses only.
                if clean_text == 'y' or clean_text == 'yes':
                    remove_notification(notification_id)
                    return 'y'
                elif clean_text == 'n' or clean_text == 'no':
                    remove_notification(notification_id)
                    return 'n'
                    
    except Exception as exception:
        print(f"Notification reading error: {exception}")
    return None

# Save exact program start time as a localized datetime object
script_start_time = datetime.now()

# 1. SENDING INITIAL MESSAGE
send_sms_question("Do you want to start the program [y/n]?")
last_sms_sent_time = time.time()

print("\nWaiting for the answer (send SMS using your watch)...")

# 2. INFINITE LOOP WAITING FOR ANSWER
while True:
    time.sleep(CHECK_INTERVAL)
    
    final_answer = check_answer_for_notification(script_start_time)
    
    if final_answer == 'y':
        print("\n✅ Your answer is: [y]")
        # --- ENTER THE CODE TO EXECUTE FOR OPTION 'y' ---
        break
        
    elif final_answer == 'n':
        print("\n❌ Your answer is: [n]")
        # --- ENTER THE CODE TO EXECUTE FOR OPTION 'n' ---
        break
        
    else:
        print("  Searching for answer... (No response yet)")
        
        # If the reminder interval has passed, check if the question is still on the screen
        if time.time() - last_sms_sent_time > REMINDER_INTERVAL:
            if is_question_notification_present():
                print("  [Anti-Spam] Question notification is still present on the phone. Skipping SMS resend.")
                # Reset the timer so we don't spam logs every loop, but keep waiting
                last_sms_sent_time = time.time() 
            else:
                print("\n⏳ Notification cleared but no answer received. Resending reminder...")
                send_sms_question("Do you want to start the program [y/N]?")
                last_sms_sent_time = time.time()  # Reset the timer

print("\nProceeding with the script...")


