from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(255))
    status = Column(String(50), default="uploaded") # uploaded, processing, completed
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")
    clauses = relationship("Clause", back_populates="document")
    risk_scores = relationship("RiskScore", back_populates="document")
    alerts = relationship("Alert", back_populates="document")

class Clause(Base):
    __tablename__ = "clauses"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    name = Column(String(100)) # Security Deposit, Notice Period, etc.
    content = Column(Text)
    detected = Column(Boolean, default=False)
    document = relationship("Document", back_populates="clauses")

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    financial_risk = Column(Integer) # 0-100
    legal_risk = Column(Integer) # 0-100
    category = Column(String(20)) # Low, Medium, High
    reason = Column(Text)
    document = relationship("Document", back_populates="risk_scores")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"))
    type = Column(String(50)) # Renewal, Notice Period
    deadline = Column(DateTime)
    status = Column(Boolean, default=False) # False=Pending, True=Done
    document = relationship("Document", back_populates="alerts")
