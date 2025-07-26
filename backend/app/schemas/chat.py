# schemas/chat.py
from pydantic import BaseModel
from typing import List, Tuple, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    user_text: str
    history: Optional[List[Tuple[str, str]]] = []  # [(user_msg, bot_msg)]

class ChatResponse(BaseModel):
    reply: str
    meta: dict
    history: List[Tuple[str, str]]  # [(user_msg, bot_reply)]
