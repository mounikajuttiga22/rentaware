from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClauseBase(BaseModel):
    name: str
    content: str
    detected: bool

class ClauseCreate(ClauseBase):
    pass

class Clause(ClauseBase):
    id: int
    doc_id: int
    class Config:
        from_attributes = True

class RiskScoreBase(BaseModel):
    financial_risk: int
    legal_risk: int
    category: str
    reason: str

class RiskScore(RiskScoreBase):
    id: int
    doc_id: int
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    type: str
    deadline: datetime
    status: bool

class Alert(AlertBase):
    id: int
    doc_id: int
    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str
    status: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    uploaded_at: datetime
    clauses: List[Clause] = []
    risk_scores: List[RiskScore] = []
    alerts: List[Alert] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    documents: List[Document] = []
    class Config:
        from_attributes = True
