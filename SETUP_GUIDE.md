# RentAware - Setup & Deployment Guide

## Overview
RentAware is an AI-powered rental agreement analyzer that:
- ✅ Analyzes rental agreements (PDF/TXT)
- ✅ Extracts critical clauses
- ✅ Calculates risk scores
- ✅ Sends SMS alerts when documents are uploaded
- ✅ Provides AI-powered chatbot for Q&A
- ✅ Stores all data in SQLite database

---

## Prerequisites
- **Python 3.8+**
- **Node.js** (if building frontend from source)
- **Ollama** (optional, for advanced AI features)
- **Twilio Account** (for SMS alerts)

---

## 1. Backend Setup

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Set Environment Variables (Optional)
Create `.env` file:
```env
DATABASE_URL=sqlite:///./rentaware.db
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+13202335382
```

### Step 3: Run the Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will start at: `http://127.0.0.1:8000`

---

## 2. Frontend Setup

### Step 1: Open Frontend
Simply open `frontend/index.html` in a web browser:
```
file:///C:/Users/Mounika/Desktop/RentAware/frontend/index.html
```

Or use Python's built-in HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Then visit: `http://127.0.0.1:8080`

---

## 3. API Endpoints

### Upload Document & Get SMS Alert
**POST** `/upload/?phone=+919876543210`
- Uploads rental agreement (PDF/TXT)
- Extracts clauses automatically
- Calculates risk scores
- Sends SMS alert immediately
- Returns: `id`, `message`, `clauses`, `alerts`

### Get Document Details
**GET** `/documents/{doc_id}`
- Fetches all document data
- Returns: clauses, risk_scores, alerts

### Chat with AI Assistant
**POST** `/chatbot/{doc_id}?query=...`
- Ask questions about the agreement
- Returns: AI-generated response

---

## 4. Using the Application

### Step 1: Upload a Document
1. Click **"Upload Agreement"** button
2. Enter your phone number (e.g., +919876543210)
3. Select a PDF or TXT file
4. System will:
   - Extract clauses
   - Calculate risk scores
   - Display alerts
   - Send SMS to your phone

### Step 2: View Analysis
- **Risk Score**: Color-coded (Green=Low, Yellow=Medium, Red=High)
- **Detected Clauses**: Shows extracted clauses
- **Alerts**: Important dates and reminders

### Step 3: Chat with AI
- Ask questions like:
  - "What is the notice period?"
  - "Are there any hidden fees?"
  - "What are my obligations?"

---

## 5. Database Schema

### Tables
- **documents**: Uploaded files
- **clauses**: Extracted contract clauses
- **risk_scores**: Financial & legal risk assessment
- **alerts**: Important deadlines
- **users**: (Optional) User accounts

Database location: `backend/rentaware.db`

---

## 6. SMS Configuration

### Option 1: Use Twilio (Recommended)
1. Sign up at https://www.twilio.com
2. Get your Account SID & Auth Token
3. Update `backend/app/services/sms_service.py`:
   ```python
   ACCOUNT_SID = "your_sid"
   AUTH_TOKEN = "your_token"
   FROM_NUMBER = "+your_twilio_number"
   ```

### Option 2: Test SMS Locally
Modify `sms_service.py`:
```python
def send_sms(phone, message):
    print(f"SMS to {phone}: {message}")
    # Add actual SMS sending when ready
```

---

## 7. Troubleshooting

### Issue: Frontend can't connect to backend
**Solution**: Ensure backend is running on `http://127.0.0.1:8000` and CORS is enabled.

### Issue: Documents not saved to database
**Solution**: Check that `uploads/` folder exists and SQLite is writable.

### Issue: SMS not sending
**Solution**: Verify Twilio credentials and phone format (+country code required).

### Issue: Chatbot not responding
**Solution**: 
- Check if Ollama is running: `http://127.0.0.1:11434`
- Or disable Ollama in `extraction.py` for regex-only analysis

---

## 8. Deployment (Production)

### Option 1: Local Network
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Access from: `http://your_ip_address:8000`

### Option 2: Docker (Advanced)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Cloud Deployment
- Deploy backend to: Heroku, AWS, Google Cloud, Azure
- Host frontend on: GitHub Pages, Vercel, Netlify
- Update API URL in `frontend/assets/js/app.js`

---

## 9. Testing

### Test Upload Endpoint
```bash
curl -X POST "http://127.0.0.1:8000/upload/?phone=%2B919876543210" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_agreement.txt"
```

### Test Document Retrieval
```bash
curl "http://127.0.0.1:8000/documents/1"
```

### Test Chatbot
```bash
curl -X POST "http://127.0.0.1:8000/chatbot/1?query=What%20is%20the%20notice%20period?"
```

---

## 10. Features Summary

✅ **Document Analysis**
- Automatic clause extraction
- Risk score calculation
- Alert detection

✅ **Mobile Notifications**
- SMS alerts on upload
- Deadline reminders every 10 seconds

✅ **AI Assistant**
- Ask questions about agreement
- Legal context-aware responses

✅ **Database**
- Persistent storage
- Full audit trail
- Easy data export

---

## Contact & Support
For issues or questions, check the logs:
```bash
tail -f app.log
```

---

**Version**: 1.0  
**Last Updated**: March 5, 2026  
**Status**: Ready for Use ✅
