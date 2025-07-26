"""
Esquemas Pydantic para las APIs del panel de tutor.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Esquemas para respuestas de alertas
class StudentInfo(BaseModel):
    id: int
    name: str
    email: str
    avatar: str

class EmotionInfo(BaseModel):
    name: str
    icon: str
    score: float

class AlertResponse(BaseModel):
    id: str
    student: StudentInfo
    lastMessage: str
    emotion: EmotionInfo
    urgency: str
    timestamp: str
    reviewed: bool

    model_config = ConfigDict(from_attributes=True)

# Esquemas para conversación de estudiante
class ConversationMessage(BaseModel):
    id: int
    sender: str  # "student" o "bot"
    text: str
    emotion: str
    timestamp: str

class StudentConversationResponse(BaseModel):
    student: StudentInfo
    conversation: List[ConversationMessage]

    model_config = ConfigDict(from_attributes=True)

# Esquemas para intervención
class InterventionRequest(BaseModel):
    student_id: int
    message: str

# Esquemas para revisión de alertas
class AlertReviewRequest(BaseModel):
    notes: Optional[str] = None
    action_taken: Optional[str] = None 