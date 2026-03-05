#!/usr/bin/env python3
"""
Direct SMS test to verify Twilio integration
"""
import sys
sys.path.insert(0, 'backend')

from app.services.sms_service import send_sms

print("\n" + "="*60)
print("🧪 DIRECT SMS TEST")
print("="*60)

phone = "+919876543210"
message = "TEST: RentAware SMS notification test"

print(f"\n📋 Test Details:")
print(f"   To: {phone}")
print(f"   Message: {message}")
print(f"\n🚀 Attempting to send SMS...")
print("-"*60)

result = send_sms(phone, message)

print("-"*60)
if result:
    print("\n✅ SMS RESULT: SUCCESS")
    print("   SMS would be sent (or sent successfully in prod)")
else:
    print("\n❌ SMS RESULT: FAILED")
    print("   There's an error preventing SMS")

print("="*60)
