import json
import os
import asyncio
import logging
import aio_pika

from datetime import datetime, date
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv


load_dotenv()

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the minimum level of logging for the logger
logger.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG

# Create handlers
file_handler = logging.FileHandler('app.log')
console_handler = logging.StreamHandler()

# Set the level for each handler
file_handler.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG
console_handler.setLevel(logging.DEBUG)  # Capture all log levels, including DEBUG

# Create formatters and add them to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def custom_json_encoder(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()  # Convert date or datetime to ISO format string


async def format_message(queue_name, data):
    if queue_name == "notifications":
        message = {
            "user_id": data.get("user_id", ""),
            "message": data.get("message", "")
        }
    elif queue_name == 'metrics':
        message = {
            "func": data.get("func", ""),
            "metadata": data.get("metadata", {}),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat())
        }
    else:
        message = {
            "user_id": data.get("user_id", ""),
            "method": data.get("method", ""),
            "args": data.get("args", {})
        }

    return json.dumps(message)


def on_retry_error(retry_state):
    logger.error(f"Failed after {retry_state.attempt_number} attempts")
    return None  # или False


class RabbitMQSender:
    def __init__(self, url):
        self.url = url
        self.connection = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.url)
            logger.info("Connected to RabbitMQ")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry_error_callback=on_retry_error)
    async def send_message(self, queue_name, data):
        try:
            await self.connect()
            message = aio_pika.Message(body=json.dumps(data).encode())

            async with self.connection.channel() as channel:
                await channel.declare_queue(queue_name, durable=True)
                await channel.default_exchange.publish(message, routing_key=queue_name)
                #logger.info(f"Sent message: {core} to RabbitMQ queue: {queue_name}")
        except Exception as e:
            logger.error(f"Error sending message to RabbitMQ queue: {queue_name}: {e}")
            raise

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
