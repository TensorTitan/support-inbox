from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class MessageCreate(BaseModel):
    conversation_id: Optional[str] = Field(
        default=None,
        description="If absent, a new conversation is created"
    )
    sender: str
    content: str


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender: str
    content: str
    created_at: datetime
