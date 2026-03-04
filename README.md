# RentAware: AI-Powered Rental Agreement Intelligence Platform

RentAware is a full-stack web application designed for hackathons to help tenants understand their rental agreements better. It identifies high-impact financial clauses, quantifies risk, and provides a decision-focused dashboard.

## 🚀 Features

- **Intelligent Extraction**: Uses `pdfplumber` and Regex to identify key clauses (Security Deposit, Notice Period, etc.).
- **Risk Scoring**: Rule-based scoring engine to categorize agreements as Low, Medium, or High risk.
- **Smart Alerts**: Extracts renewal and notice deadlines and stores them for reminders.
- **AI Chatbot**: Document-grounded chatbot to answer specific tenant queries about the agreement.
- **Premium Dashboard**: Responsive UI with visual risk indicators and modular layout.

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla), Chart.js
- **Backend**: Python, FastAPI, SQLAlchemy, MySQL
- **Extraction**: pdfplumber, Regex
- **AI**: OpenAI / Gemini API

## 📋 Prerequisites

- Python 3.9+
- MySQL Server
- OpenAI API Key (Optional, mock responses provided)

## 🔧 Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/RentAware.git
   cd RentAware
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Configuration**:
   - Create a MySQL database named `rentaware_db`.
   - Update `.env` with your credentials:
     ```env
     DATABASE_URL=mysql+mysqlconnector://root:password@localhost/rentaware_db
     OPENAI_API_KEY=your_api_key
     ```

4. **Run the Application**:
   - **Backend**:
     ```bash
     uvicorn app.main:app --reload
     ```
   - **Frontend**:
     - Open `frontend/index.html` in your browser.

## 🏗 Project Structure

```text
RentAware/
├── backend/
│   ├── app/
│   │   ├── api/          # API Route definitions
│   │   ├── services/     # Extraction, Scoring, Chatbot logic
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schemas.py     # Pydantic schemas
│   │   └── main.py       # FastAPI entry point
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── index.html
└── README.md
```

## ⚖️ License
MIT License
