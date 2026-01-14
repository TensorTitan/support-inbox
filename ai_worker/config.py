import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

AMQP_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/%2F"

EVENT_EXCHANGE = os.getenv("EVENT_EXCHANGE", "events")
ROUTING_KEY = os.getenv("MESSAGE_RECEIVED_ROUTING_KEY", "MessageReceived")
QUEUE_NAME = os.getenv("AI_QUEUE_NAME", "ai.message_received")
