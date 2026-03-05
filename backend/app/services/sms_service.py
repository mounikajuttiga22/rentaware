from twilio.rest import Client
from datetime import datetime
import os

# Twilio credentials
ACCOUNT_SID = "AC5b89d46f37ed2e5e91e1f6af9f12bd2b"
AUTH_TOKEN = "b023dc262d781dc53636fd75f322f7d7"
FROM_NUMBER = "+13202335382"

# Mock SMS log file
SMS_LOG_FILE = os.path.join(os.path.dirname(__file__), "../../sms_log.txt")

# Create log file if doesn't exist
os.makedirs(os.path.dirname(SMS_LOG_FILE), exist_ok=True)

# Use Twilio or mock
USE_MOCK = False  # Set to False to use real Twilio

print(f"\n{'='*60}")
print(f"SMS SERVICE INITIALIZATION")
print(f"{'='*60}")
print(f"Mode: {'MOCK SMS (logs to file)' if USE_MOCK else 'REAL TWILIO'}")
print(f"Log File: {SMS_LOG_FILE}")
print(f"{'='*60}\n")

if not USE_MOCK:
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        print(f"✓ Twilio Client Connected\n")
    except Exception as e:
        print(f"⚠️  Twilio error: {e}\n")
        client = None
else:
    client = None


def log_sms(phone, message):
    """Log SMS to file"""
    try:
        with open(SMS_LOG_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{'─'*70}\n")
            f.write(f"[{timestamp}] SMS SENT\n")
            f.write(f"{'─'*70}\n")
            f.write(f"From: {FROM_NUMBER}\n")
            f.write(f"To:   {phone}\n")
            f.write(f"Message:\n{message}\n")
            f.write(f"{'─'*70}\n\n")
        return True
    except Exception as e:
        print(f"Error writing to SMS log: {e}")
        return False


def send_sms(phone, message):
    """
    Send SMS notification
    In mock mode: logs to file
    In real mode: sends via Twilio
    """
    print(f"\n📱 SMS Service Called:")
    print(f"   To: {phone}")
    print(f"   Message: {message[:50]}...")

    if not phone:
        print(f"   ❌ ERROR: Phone is empty!")
        return False

    if USE_MOCK:
        # Mock mode - log to file
        print(f"   Mode: MOCK (logging to file)")
        success = log_sms(phone, message)
        if success:
            print(f"   ✅ SMS logged to: {SMS_LOG_FILE}")
            print(f"   Check the file to see sent SMS")
            # Also print to console
            print(f"\n   📧 SMS CONTENT:")
            print(f"   {'─'*50}")
            print(f"   From: {FROM_NUMBER}")
            print(f"   To: {phone}")
            print(f"   Message:\n   {message}")
            print(f"   {'─'*50}\n")
            return True
        else:
            print(f"   ❌ Failed to log SMS")
            return False

    else:
        # Real Twilio mode
        if not client:
            print(f"   ❌ Twilio client not available")
            return False

        try:
            print(f"   🔄 Sending via Twilio...")
            sms = client.messages.create(
                body=message,
                from_=FROM_NUMBER,
                to=phone
            )
            print(f"   ✅ SMS SENT!")
            print(f"   SID: {sms.sid}")
            return True

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Twilio Error: {error_msg}")

            if "unverified" in error_msg.lower():
                print(f"\n   ⚠️  PHONE NOT VERIFIED IN TWILIO")
                print(f"   To send real SMS:")
                print(f"   1. Go to https://www.twilio.com/console")
                print(f"   2. Verify your phone number")
                print(f"   OR switch back to MOCK mode (USE_MOCK = True)")

            return False
