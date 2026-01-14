import json
import os
import time
import pika
import requests


# Configuration

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

EVENT_EXCHANGE = os.getenv("EVENT_EXCHANGE", "events")

CONSUME_KEY = os.getenv("MESSAGE_RECEIVED_ROUTING_KEY", "message.created")
PUBLISH_KEY = "ai.completed"
QUEUE_NAME = os.getenv("AI_QUEUE_NAME", "ai.message_received")

MESSAGING_BASE_URL = (
    os.getenv("MESSAGING_BASE_URL")
    or os.getenv("MESSAGING_URL")
    or "http://messaging:8000"
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")


# Helpers

def extract_json(text: str) -> dict:
    """
    Extract the first JSON object found in text.
    Handles extra text, markdown fences, explanations, etc.
    """
    if not text:
        raise ValueError("Empty AI response")

    # Remove ``` fences if present
    clean = text.strip()
    if clean.startswith("```"):
        clean = clean.strip("`").strip()
        if clean.lower().startswith("json"):
            clean = clean[4:].strip()

    start = clean.find("{")
    end = clean.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")

    snippet = clean[start:end + 1]
    return json.loads(snippet)

def call_ollama(prompt: str, timeout=180) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "top_p": 1,
            },
        },
        timeout=timeout,
    )

    if not r.ok:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text}")

    return r.json().get("response", "")

# AI logic

def run_ai(event: dict) -> dict:
    prompt = f"""
Return ONLY a valid JSON object.

The JSON schema:
{{
  "intent": "string",
  "summary": "string",
  "suggested_reply": "string"
}}

No markdown.
No explanations.
No extra text.

Message:
{event.get("content", "")}
""".strip()

    raw = call_ollama(prompt)
    print("[ai_worker] raw ollama response:\n", raw)

    try:
        result = extract_json(raw)
    except Exception as first_error:
        print("[ai_worker] invalid JSON, retrying repair")

        fix_prompt = f"""
Fix this into valid JSON ONLY.
No explanations.
No markdown.

{raw}
""".strip()

        repaired = call_ollama(fix_prompt, timeout=60)
        print("[ai_worker] repaired response:\n", repaired)

        result = extract_json(repaired)

    return {
        "conversation_id": event["conversation_id"],
        "message_id": event["message_id"],
        "intent": result.get("intent", "unknown"),
        "summary": result.get("summary", ""),
        "suggested_reply": result.get("suggested_reply", ""),
    }


# RabbitMQ connection
def connect():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=30,
        )
    )

# Main loop

def main():
    print("[ai_worker] starting")
    print(f"[ai_worker] messaging: {MESSAGING_BASE_URL}")
    print(f"[ai_worker] ollama: {OLLAMA_URL} model={OLLAMA_MODEL}")
    print(f"[ai_worker] consume: {CONSUME_KEY} queue={QUEUE_NAME}")

    while True:
        try:
            connection = connect()
            channel = connection.channel()

            channel.exchange_declare(
                exchange=EVENT_EXCHANGE,
                exchange_type="topic",
                durable=True,
            )

            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(
                exchange=EVENT_EXCHANGE,
                queue=QUEUE_NAME,
                routing_key=CONSUME_KEY,
            )

            print("[ai_worker] listening for message.created")

            def callback(ch, method, properties, body):
                event = json.loads(body)
                print("[ai_worker] received message", event.get("message_id"))

                try:
                    ai = run_ai(event)

                    # Store AI result
                    url = f"{MESSAGING_BASE_URL}/ai-insights"
                    resp = requests.post(url, json=ai, timeout=20)

                    if not resp.ok:
                        raise RuntimeError(
                            f"POST {url} failed {resp.status_code}: {resp.text}"
                        )

                    # Notify gateway
                    ch.basic_publish(
                        exchange=EVENT_EXCHANGE,
                        routing_key=PUBLISH_KEY,
                        body=json.dumps({
                            "conversation_id": ai["conversation_id"],
                            "message_id": ai["message_id"],
                            "ai": {
                                "intent": ai["intent"],
                                "summary": ai["summary"],
                                "suggested_reply": ai["suggested_reply"],
                            },
                        }),
                    )

                    print("[ai_worker] stored ai-insights + published ai.completed")

                except Exception as e:
                    print("[ai_worker] AI failed:", e)

                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()

        except Exception as e:
            print("[ai_worker] retrying in 5s:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
