import subprocess, json, time
from datetime import datetime

PHONE_NUM = "518185058" # !ENTER YOUR PHONE NUMBER!
num_of_tries = 10
break_between_tries_val = 3
timeout_val = break_between_tries_val * num_of_tries

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
                # This prevents picking up random words containing 'y' or 'n'.
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

# 1. SENDING MESSAGE
send_sms_question("Do you want to start the program [y/N]?")

print("\nWaiting for the answer (send SMS using your watch)...")

# Variable to keep track of the final user response
final_answer = None

# 2. VALIDATING LOOP
for i in range(num_of_tries): 
    time.sleep(break_between_tries_val)
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
        print(f"  [Try {i+1}/{num_of_tries}] Searching for answer...")

# 3. TIMEOUT HANDLING
if final_answer is None:
    print(f"\n⏳ Timeout: No reply received within {timeout_val} seconds.")


