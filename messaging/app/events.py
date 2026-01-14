import json
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
EVENT_EXCHANGE = os.getenv("EVENT_EXCHANGE", "events")


def publish_event(routing_key: str, payload: dict):
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=30,
        )

        connection = pika.BlockingConnection(params)
        channel = connection.channel()


        channel.exchange_declare(
            exchange=EVENT_EXCHANGE,
            exchange_type="topic",
            durable=True,
        )


        channel.queue_declare(
            queue="ai.message_received",
            durable=True,
        )
        channel.queue_bind(
            exchange=EVENT_EXCHANGE,
            queue="ai.message_received",
            routing_key="message.created",
        )

        channel.basic_publish(
            exchange=EVENT_EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()

        print(f"[events] published {routing_key}")

    except Exception as e:
        print(f"[events] WARNING: failed to publish event {routing_key}: {e}")
