from pydantic import BaseModel
from typing import List, Optional

class AskRequest(BaseModel):
    question: str

class Evidence(BaseModel):
    message_id: Optional[str] = None
    snippet: str

class AskResponse(BaseModel):
    answer: str
    confidence: float
    evidence: List[Evidence] = []

class Message(BaseModel):
    id: str
    member_name: str
    text: str
    timestamp: Optional[str] = None
