# 📱 SMS Not Arriving? Fix Guide

## ⚠️ The Problem
Twilio **trial accounts** can only send SMS to **verified phone numbers**. Your phone number needs to be verified first.

---

## ✅ SOLUTION 1: Verify Your Phone Number (Recommended)

### Step 1: Go to Twilio Console
```
https://www.twilio.com/console
```

### Step 2: Navigate to Phone Numbers
1. Login to your Twilio account
2. Click your **avatar** (top right)
3. Select **Account** or **Phone Numbers**
4. Look for **"Verified Numbers"** or **"Verified Caller IDs"**

### Step 3: Add Your Number
1. Click **"Add a Verified Number"** or **"Verify a Number"**
2. Enter your phone number: **+919876543210** (or your actual number)
3. Choose verification method:
   - **Call verification** - Twilio calls you with code
   - **SMS verification** - Twilio texts you a code
4. Enter the code you receive
5. Done! ✅

### Step 4: Wait 15 Minutes
After verification, wait ~15 minutes for Twilio to propagate the change.

### Step 5: Try Upload Again
1. Start backend: `start_backend.bat`
2. Upload document with your verified phone number
3. **SMS should arrive!** ✅

---

## 🛠️ SOLUTION 2: Debug Mode (Test Without SMS)

If you want to test without sending real SMS, use debug mode:

### Quick Switch
```
File: backend/app/services/sms_service.py
Line: 11

Change:
  DEBUG_SMS = False
To:
  DEBUG_SMS = True
```

### What Happens
- SMS will print to **console/terminal** instead of sending
- Perfect for testing the system
- Allows you to see what SMS *would* be sent

### Example Output
```
📱 [DEBUG MODE] SMS Would Be Sent:
   To: +919876543210
   Message: RentAware: Your rental agreement has been uploaded and analyzed. 2 alerts detected. Check your dashboard.
   From: +13202335382
```

### Switching Back
Change `DEBUG_SMS = True` → `DEBUG_SMS = False` to send real SMS again.

---

## 🔍 SOLUTION 3: Check Twilio Credentials

Your Twilio credentials in the code:
```
Account SID: AC5b89d46f37ed2e5e91e1f6af9f12bd2b
Auth Token: b023dc262d781dc53636fd75f322f7d7
From Number: +13202335382
```

### Verify They're Correct
1. Go to https://www.twilio.com/console
2. Check your **Account SID** matches
3. Check your **Auth Token** matches
4. Check your **Phone Number** (From Number) is active

If they don't match, update `backend/app/services/sms_service.py`:
```python
ACCOUNT_SID = "YOUR_ACCOUNT_SID"
AUTH_TOKEN = "YOUR_AUTH_TOKEN"
FROM_NUMBER = "+1234567890"  # Your Twilio phone number
```

---

## 📋 Quick Checklist

- [ ] Is your phone number verified in Twilio? → https://twilio.com/console
- [ ] Are you entering the correct phone number when uploading?
- [ ] Is backend running? (`start_backend.bat` or `python -m uvicorn...`)
- [ ] Are SMS error messages showing in terminal?
- [ ] Have you waited 15+ minutes after verification?
- [ ] Is your phone number format correct? (e.g., +919876543210)

---

## 🚀 Test It

### Option A: Real SMS (After Verification)
```bash
# Backend running
start_backend.bat

# From another terminal:
python integration_test.py
# SMS should arrive on verified number
```

### Option B: Debug Mode (Immediate Test)
```bash
# Edit:
backend/app/services/sms_service.py
# Set: DEBUG_SMS = True

# Run:
start_backend.bat
python integration_test.py

# Check terminal output - SMS will print there
```

---

## ❓ Still Not Working?

### Check Terminal Output
When you upload and SMS should send, check the backend terminal for:

#### ✅ Success
```
✅ SMS SENT to +919876543210 | SID: SMxxxxxxxxxxxxxxxxxxxxxxxx
```

#### ⚠️ Trial Account Issue
```
⚠️  TWILIO TRIAL ACCOUNT - PHONE NOT VERIFIED
Message would have been sent to: +919876543210
```
→ Verify your phone in Twilio console

#### ❌ Invalid Credentials
```
❌ SMS ERROR: [31008] Invalid phone number
```
→ Check phone number format or credentials

---

## 📞 Twilio Support
- Account Dashboard: https://www.twilio.com/console
- Documentation: https://www.twilio.com/docs/sms
- Trial Account Info: https://www.twilio.com/console/sms/settings/trial-numbers

---

## 🎯 Next Steps

1. **Verify your phone number** in Twilio (5 minutes)
2. **Wait 15 minutes** for propagation
3. **Upload a document** with your verified number
4. **SMS arrives!** 🎉

Once verified, all future uploads will send SMS automatically.

Good luck! 📱✨
