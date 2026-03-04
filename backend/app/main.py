from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from . import models, schemas, database
from .services import extraction, scoring, chatbot

app = FastAPI(title="RentAware API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to RentAware API"}

@app.post("/upload/", response_model=schemas.Document)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # Save the file locally
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document entry in DB
    db_document = models.Document(filename=file.filename, file_path=file_path, status="uploaded")
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Process document
    await process_document_task(db_document.id, db)
    
    return db_document

async def process_document_task(doc_id: int, db: Session):
    # 1. Extract text and detect clauses
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        return
    
    doc.status = "processing"
    db.commit()
    
    extracted_data = extraction.extract_and_detect(doc.file_path)
    
    # Save clauses
    for clause_name, clause_content in extracted_data["clauses"].items():
        db_clause = models.Clause(
            doc_id=doc_id,
            name=clause_name,
            content=clause_content,
            detected=True if clause_content else False
        )
        db.add(db_clause)
    
    # 2. Risk Scoring
    risk_info = scoring.calculate_risk(extracted_data["clauses"])
    db_risk = models.RiskScore(
        doc_id=doc_id,
        financial_risk=risk_info["financial_risk"],
        legal_risk=risk_info["legal_risk"],
        category=risk_info["category"],
        reason=risk_info["reason"]
    )
    db.add(db_risk)
    
    # 3. Smart Alerts
    alerts = extraction.extract_alerts(extracted_data["clauses"])
    for alert in alerts:
        db_alert = models.Alert(
            doc_id=doc_id,
            type=alert["type"],
            deadline=alert["deadline"],
            status=False
        )
        db.add(db_alert)
    
    doc.status = "completed"
    db.commit()

@app.get("/documents/{doc_id}", response_model=schemas.Document)
def get_document(doc_id: int, db: Session = Depends(database.get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.post("/chatbot/{doc_id}")
async def chatbot_query(doc_id: int, query: str, db: Session = Depends(database.get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get all clauses as context
    clauses = db.query(models.Clause).filter(models.Clause.doc_id == doc_id).all()
    context = "\n".join([f"{c.name}: {c.content}" for c in clauses])
    
    response = await chatbot.get_response(query, context)
    return {"response": response}
