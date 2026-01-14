from pydantic import BaseModel

class AIInsightCreate(BaseModel):
    message_id: str
    conversation_id: str
    intent: str = "unknown"
    summary: str = ""
    suggested_reply: str = ""