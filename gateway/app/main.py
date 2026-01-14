import asyncio
import json

import httpx
import jwt
import aio_pika
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from .config import settings



JWT_SECRET = settings.jwt_secret
JWT_ALG = "HS256"
MESSAGING_URL = "http://messaging:8000"
AMQP_URL = "amqp://guest:guest@rabbitmq/"



app = FastAPI(title="Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

connections: set[WebSocket] = set()



def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_token(token)



@app.post("/login")
async def login(data: dict):
    if data.get("username") != "operator1" or data.get("password") != "test123":
        raise HTTPException(status_code=401, detail="Bad credentials")

    token = jwt.encode(
        {"sub": "operator1", "role": "operator"},
        JWT_SECRET,
        algorithm=JWT_ALG,
    )

    return {"access_token": token, "token_type": "bearer"}



@app.post("/messages")
async def send_message(body: dict, user=Depends(get_current_user)):
    payload = {
        "conversation_id": body.get("conversation_id"),
        "sender": user["sub"],
        "content": body.get("content"),
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{MESSAGING_URL}/messages",
            json=payload,
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()



@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=1008)
        return

    try:
        user = decode_token(token)
    except HTTPException:
        await ws.close(code=1008)
        return

    await ws.accept()
    connections.add(ws)
    print("[gateway] websocket connected")

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)

            payload = {
                "conversation_id": data.get("conversation_id"),
                "sender": user["sub"],
                "content": data.get("content"),
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{MESSAGING_URL}/messages",
                    json=payload,
                )

            if resp.status_code != 200:
                await ws.send_json({"type": "error", "detail": resp.text})
                continue

            await broadcast({
                "type": "message_stored",
                "message": resp.json(),
            })

    except WebSocketDisconnect:
        connections.discard(ws)
        print("[gateway] websocket disconnected")



async def broadcast(event: dict):
    dead = []
    for ws in connections:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)

    for ws in dead:
        connections.discard(ws)



async def listen_for_ai_completed():
    while True:
        try:
            print("[gateway] connecting to RabbitMQ...")
            connection = await aio_pika.connect_robust(AMQP_URL)

            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                "events",
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )

            queue = await channel.declare_queue("", exclusive=True)
            await queue.bind(exchange, routing_key="ai.completed")

            print("[gateway] listening for ai.completed events")

            async with queue.iterator() as q:
                async for message in q:
                    async with message.process():
                        payload = json.loads(message.body)


                        await broadcast({
                            "type": "ai_completed",
                            "message": {
                                "id": payload["message_id"],
                                "conversation_id": payload["conversation_id"],
                                "ai": {
                                    "intent": payload.get("intent"),
                                    "summary": payload.get("summary"),
                                    "suggested_reply": payload.get("suggested_reply"),
                                }
                            }
                        })

        except Exception as e:
            print("[gateway] rabbit listener error, retrying in 3s:", e)
            await asyncio.sleep(3)



@app.on_event("startup")
async def startup():
    asyncio.create_task(listen_for_ai_completed())



