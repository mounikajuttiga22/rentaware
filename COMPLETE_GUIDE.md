# 🎉 RentAware - Complete Setup & Deployment Guide

## ✅ What's Working Now

✨ **100% Integration Complete:**
- ✓ Backend API running
- ✓ Frontend UI connected
- ✓ Document upload & processing
- ✓ Risk assessment calculating
- ✓ Alerts detecting
- ✓ Database storing data
- ✓ AI chatbot responding
- ✓ SMS integration ready

---

## 🚀 Quick Start

### 1️⃣ Start Backend Server
```bash
cd backend
pip install -r requirements.txt
$env:PYTHONPATH="C:\Users\Mounika\Desktop\RentAware\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ Start Frontend Server (New Terminal)
```bash
python run_frontend.py
```
This automatically opens your browser at `http://127.0.0.1:8080`

### 3️⃣ Test Everything
```bash
python integration_test.py
```

---

## 📱 SMS Configuration

### Option A: Use Your Own Twilio Account (Recommended)

1. **Create Twilio Account:**
   - Go to https://www.twilio.com/try-twilio
   - Sign up for free trial
   - Get your Account SID and Auth Token

2. **Update Credentials:**
   - Edit `backend/app/services/sms_service.py`
   - Replace:
     ```python
     ACCOUNT_SID = "your_account_sid"
     AUTH_TOKEN = "your_auth_token"
     FROM_NUMBER = "your_twilio_number"
     ```

3. **Verify Phone Numbers:**
   - To send SMS in trial mode, verify numbers at:
   - https://www.twilio.com/user/account/phone-numbers/verified

### Option B: Test SMS Without Verification

The system now handles Twilio trial limitations:
- SMS attempts logging instead of failing
- Shows exactly what message would be sent
- Works with unverified numbers (logs to console)

### Option C: Mock SMS for Development

To disable SM entirely for testing, edit `sms_service.py`:
```python
def send_sms(phone, message):
    print(f"📱 SMS (MOCK): {message}")
    return True
```

---

## 🎯 Complete Workflow

### Step 1: Upload Document
```
1. Click "Upload Agreement" button
2. Enter your phone number (with country code, e.g., +919876543210)
3. Select PDF or TXT file
4. Wait for processing...
```

### Step 2: Get Results
```
Backend processes:
✓ Extracts clauses
✓ Calculates risk scores
✓ Detects important alerts
✓ Sends SMS notification (if Twilio configured)
```

### Step 3: View Dashboard
```
Frontend displays:
✓ Risk assessment (low/medium/high)
✓ 6 key clauses (security deposit, notice period, etc.)
✓ Important deadlines
✓ Extract key information
```

### Step 4: Ask AI Assistant
```
Chat with document:
- "What is the security deposit?"
- "What's the notice period?"
- "Are there any penalties?"
- "When does renewal happen?"
```

---

## 🗄️ Database

Location: `backend/rentaware.db` (SQLite)

**Tables:**
- `documents` - Uploaded files
- `clauses` - Extracted contract terms
- `risk_scores` - Financial & legal risk
- `alerts` - Important deadlines
- `users` - (Optional) User accounts

---

## 📊 API Endpoints

### Upload Document
```bash
POST /upload/?phone=+919876543210
Content-Type: multipart/form-data
Body: file (PDF/TXT)
```

### Get Document Data
```bash
GET /documents/{id}
```

### Chat with AI
```bash
POST /chatbot/{id}?query=your%20question
```

---

## 🧪 Testing

### Test Individual Endpoints

**1. Health Check:**
```bash
curl http://127.0.0.1:8000/
```

**2. Upload Document:**
```bash
python integration_test.py
```

**3. Check Logs:**
- Backend: Terminal showing uvicorn output
- Frontend: Browser console (F12)

---

## 🐛 Troubleshooting

### Issue: "Backend not responding"
**Solution:**
```bash
# Make sure backend is running
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: "SMS not sending"
**Solution:**
- Check Twilio credentials are correct
- Verify phone number at twilio.com
- Check backend logs for error message
- Use mock SMS for testing

### Issue: "Document not processing"
**Solution:**
- Ensure file is PDF or TXT
- Check file size < 10MB
- Look at backend logs
- Try with sample_agreement.txt

### Issue: "AI Assistant not responding"
**Solution:**
- Ollama is optional (not required)
- System works without it
- Backend uses regex extraction as fallback

---

## 📈 Production Deployment

### Deploy Backend
```bash
# Heroku
heroku login
heroku create your-app-name
git push heroku main

# AWS
aws lambda create-function --runtime python3.9 ...

# Google Cloud
gcloud functions deploy upload --runtime python39 ...
```

### Deploy Frontend
```bash
# GitHub Pages
git push origin gh-pages

# Vercel
vercel deploy

# Netlify
netlify deploy --prod --dir=frontend
```

### Environment Variables
```bash
# Create .env in backend folder
DATABASE_URL=sqlite:///./rentaware.db
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE=+1234567890
```

---

## ✨ Features

### Document Analysis
- 6 Key Clauses Detected
  - Security Deposit
  - Notice Period
  - Lock-in Period
  - Late Fees
  - Maintenance Charges
  - Renewal Options

### Risk Assessment
- Financial Risk (0-100)
- Legal Risk (0-100)
- Risk Category (Low/Medium/High)
- Detailed Explanation

### Alerts
- Automatic deadline detection
- Days remaining calculation
- SMS notifications
- Persistent storage

### AI Assistant
- Ask questions about agreement
- Context-aware responses
- Legal terminology support
- Available 24/7

---

## 🎨 Customization

### Change Colors
Edit `frontend/assets/css/style.css`:
```css
:root {
    --primary: #6366f1;  /* Change this */
    --secondary: #8b5cf6;
    --success: #10b981;
    ...
}
```

### Change SMS Message
Edit `backend/app/main.py` in upload endpoint:
```python
sms_message = "Your custom message here"
```

### Add New Clauses
Edit `backend/app/services/extraction.py`:
```python
"Your Clause Name": [r"keyword1", r"keyword2"]
```

---

## 📞 Support

### Common Tasks

**Check Backend Logs:**
```bash
tail -f backend.log
```

**Reset Database:**
```bash
rm backend/rentaware.db
```

**Clear Cache:**
```bash
rm -rf __pycache__ .pytest_cache
```

**Update Dependencies:**
```bash
pip install -r backend/requirements.txt --upgrade
```

---

## 🔒 Security Notes

1. **Never commit credentials:**
   - Use `.env` files
   - Add to `.gitignore`

2. **Use environment variables:**
   ```python
   import os
   ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
   ```

3. **Validate input:**
   - Check file types
   - Limit file size
   - Sanitize phone numbers

4. **HTTPS in production:**
   - Use SSL certificates
   - Update CORS settings
   - Validate requests

---

## 📚 Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Twilio
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Database:** SQLite
- **AI:** Ollama (optional), Regex extraction
- **Scheduling:** APScheduler
- **SMS:** Twilio API

---

## ✅ Checklist Before Going Live

- [ ] Backend running on 0.0.0.0:8000
- [ ] Frontend accessible and styled
- [ ] Database initialized (rentaware.db)
- [ ] SMS configured (or disabled gracefully)
- [ ] Tests passing (integration_test.py)
- [ ] Error handling working
- [ ] CORS enabled
- [ ] Logging configured
- [ ] Security checks done
- [ ] Documentation complete

---

## 🎉 You're All Set!

Your RentAware application is fully functional and ready to use!

**Start now:**
```bash
python run_frontend.py
```

**Enjoy analyzing rental agreements! 🏠📋✨**
