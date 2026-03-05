from fastapi import FastAPI, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import uuid

from app.database import engine, get_db, Base
from app.models import Document, Clause, RiskScore, Alert, User
from app.services.extraction import extract_and_detect
from app.services.scheduler_service import update_alerts, start_scheduler
from app.services.chatbot import get_response
from app.services.sms_service import send_sms

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.on_event("startup")
def start_background_scheduler():
    print("Starting scheduler...")
    start_scheduler()


@app.get("/")
def home():
    return {"message": "Rental Agreement AI Analyzer API Running"}


@app.post("/upload/")
async def upload(file: UploadFile = File(...), phone: str = Query(None), db: Session = Depends(get_db)):
    """Upload and process a rental agreement"""
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create document record
    doc = Document(
        filename=file.filename,
        file_path=file_path,
        status="processing"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Extract and detect
    result = extract_and_detect(file_path)
    print("Detected alerts:", result["alerts"])

    # Save clauses
    for clause in result.get("clauses", []):
        db_clause = Clause(
            doc_id=doc.id,
            name=clause.get("name", ""),
            content=clause.get("content", ""),
            detected=clause.get("detected", False)
        )
        db.add(db_clause)

    # Save risk scores
    for risk in result.get("risk_scores", []):
        db_risk = RiskScore(
            doc_id=doc.id,
            financial_risk=risk.get("financial_risk", 0),
            legal_risk=risk.get("legal_risk", 0),
            category=risk.get("category", ""),
            reason=risk.get("reason", "")
        )
        db.add(db_risk)

    # Save alerts
    from datetime import datetime
    for alert in result.get("alerts", []):
        deadline_str = alert.get("deadline")
        # Parse deadline if it's a string (ISO format)
        if isinstance(deadline_str, str):
            deadline = datetime.fromisoformat(deadline_str)
        else:
            deadline = deadline_str
            
        db_alert = Alert(
            doc_id=doc.id,
            type=alert.get("type", ""),
            deadline=deadline
        )
        db.add(db_alert)

    db.commit()
    doc.status = "completed"
    db.commit()

    # Send SMS immediately if phone number provided
    print(f"\n🔍 SMS DEBUG INFO:")
    print(f"  Phone received: {phone}")
    print(f"  Phone type: {type(phone)}")
    print(f"  Phone is None: {phone is None}")
    print(f"  Phone is empty: {phone == ''}")
    
    if phone and phone.strip():  # Check both for None and empty string
        sms_message = f"RentAware: Your rental agreement has been uploaded and analyzed. {len(result.get('alerts', []))} alerts detected. Check your dashboard."
        print(f"  Sending SMS to: {phone}")
        print(f"  Message: {sms_message}")
        result_sms = send_sms(phone, sms_message)
        print(f"  SMS Result: {result_sms}\n")
    else:
        print(f"  ⚠️  Phone number not provided or empty. SMS not sent.\n")

    update_alerts(result["alerts"])

    return {
        "id": doc.id,
        "message": "File processed successfully",
        "clauses": result["clauses"],
        "alerts": result["alerts"]
    }


@app.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Fetch document data with all related information"""
    
    document = db.query(Document).filter(Document.id == doc_id).first()
    
    if not document:
        return {"error": "Document not found"}

    clauses = db.query(Clause).filter(Clause.doc_id == doc_id).all()
    risks = db.query(RiskScore).filter(RiskScore.doc_id == doc_id).all()
    alerts = db.query(Alert).filter(Alert.doc_id == doc_id).all()

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "uploaded_at": document.uploaded_at,
        "clauses": [
            {
                "id": c.id,
                "name": c.name,
                "content": c.content,
                "detected": c.detected
            }
            for c in clauses
        ],
        "risk_scores": [
            {
                "id": r.id,
                "financial_risk": r.financial_risk,
                "legal_risk": r.legal_risk,
                "category": r.category,
                "reason": r.reason
            }
            for r in risks
        ],
        "alerts": [
            {
                "id": a.id,
                "type": a.type,
                "deadline": a.deadline.isoformat() if a.deadline else None,
                "status": a.status
            }
            for a in alerts
        ]
    }


@app.post("/chatbot/{doc_id}")
async def chatbot(doc_id: int, query: str = Query(...), db: Session = Depends(get_db)):
    """Get AI response about the document"""
    
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        return {"error": "Document not found"}

    # Read the document content
    try:
        with open(document.file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        content = "Unable to read document content"

    # Get AI response
    response = await get_response(query, content)

    return {"response": response}