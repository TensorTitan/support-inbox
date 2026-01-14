from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

class AIInsight(Base):
    __tablename__ = "ai_insights"

    # Use message_id as PK so it's 1:1 with Message
    message_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)

    intent: Mapped[str] = mapped_column(String(64), default="unknown")
    summary: Mapped[str] = mapped_column(Text, default="")
    suggested_reply: Mapped[str] = mapped_column(Text, default="")

