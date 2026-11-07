import json
import os
import pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME   = os.environ.get("QUEUE_NAME",   "games")


class Publisher:
    def __init__(self):
        self._connection = None
        self._channel = None

    def _connect(self) -> None:
        self._connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def publish(self, message: dict) -> None:
        if self._connection is None or self._connection.is_closed:
            self._connect()
        self._channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )


publisher = Publisher()
