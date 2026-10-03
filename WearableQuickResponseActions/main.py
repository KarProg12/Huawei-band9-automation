#!/usr/bin/env python
import subprocess
import shlex

MY_PHONE_NUM = "+48518185058"  # Enter your phone number
CONTENT = input("\nEnter mesaage you want to send to wearable:"
                "\n>>> ")

cmd = f"termux-sms-send -n {MY_PHONE_NUM} {shlex.quote(CONTENT)}"
subprocess.run(shlex.split(cmd))
