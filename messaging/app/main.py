from datetime import datetime, timezone

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from .models import Conversation, Message
from .schemas import MessageCreate, MessageOut
from .events import publish_event
from .config import MESSAGE_RECEIVED_ROUTING_KEY
from .ai_schemas import AIInsightCreate
from .ai_models import AIInsight



app = FastAPI(title="Messaging")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/health")
def health():
    return {"status": "ok", "service": "messaging"}



@app.post("/messages", response_model=MessageOut)
def create_message(payload: MessageCreate, db: Session = Depends(get_db)):
    if payload.conversation_id:
        conv = db.get(Conversation, payload.conversation_id)
        if conv is None:
            conv = Conversation(id=payload.conversation_id)
            db.add(conv)
            db.commit()
            db.refresh(conv)
    else:
        conv = Conversation()
        db.add(conv)
        db.commit()
        db.refresh(conv)

    msg = Message(
        conversation_id=conv.id,
        sender=payload.sender,
        content=payload.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    event = {
        "conversation_id": msg.conversation_id,
        "message_id": msg.id,
        "sender": msg.sender,
        "content": msg.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    publish_event(MESSAGE_RECEIVED_ROUTING_KEY, event)

    return MessageOut(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender=msg.sender,
        content=msg.content,
        created_at=msg.created_at,
    )



@app.post("/ai-insights")
def create_ai_insight(
    data: AIInsightCreate,
    db: Session = Depends(get_db),
):
    ai = AIInsight(
        message_id=data.message_id,
        conversation_id=data.conversation_id,
        intent=data.intent,
        summary=data.summary,
        suggested_reply=data.suggested_reply,
    )

    db.merge(ai)  # upsert (important)
    db.commit()

    return {"status": "ok"}



@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )

    result = []
    for msg in messages:
        ai = db.get(AIInsight, msg.id)
        result.append({
            "id": msg.id,
            "sender": msg.sender,
            "content": msg.content,
            "created_at": msg.created_at,
            "ai": None if not ai else {
                "intent": ai.intent,
                "summary": ai.summary,
                "suggested_reply": ai.suggested_reply,
            }
        })

    return {
        "conversation_id": conversation_id,
        "messages": result,
    }
