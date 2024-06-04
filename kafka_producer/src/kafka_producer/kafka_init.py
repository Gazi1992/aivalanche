from datetime import datetime
import asyncio
from aiokafka import AIOKafkaProducer
import json

# kafka server
# KAFKA_SERVER = "de.kafka:29092"
KAFKA_SERVER = "kafka:9092"

async def send_event(ORDER_KAFKA_TOPIC, data):
    async with AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER, acks="all") as producer:
        # Encode data as JSON bytes
        message_bytes = json.dumps(data).encode("utf-8")
        # Send message to Kafka topic
        await producer.send(ORDER_KAFKA_TOPIC, message_bytes)
        # Flush producer to ensure messages are sent
        await producer.flush()
 
