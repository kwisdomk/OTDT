"""
Kafka consumer for sensor telemetry.
Consumes from 'sensor.telemetry' topic and forwards to message handler.
"""

import json
import os
from kafka import KafkaConsumer
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('KAFKA_TOPIC_SENSORS', 'sensor.telemetry')
GROUP_ID = 'otdt-api-group'

async def consume(handler):
    """
    Async Kafka consumer that calls handler(message) for each message.
    Runs in a background asyncio task.
    """
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP,
            value_deserializer=lambda b: json.loads(b.decode('utf-8')),
            auto_offset_reset='latest',
            group_id=GROUP_ID,
            enable_auto_commit=True,
        )
        print(f'[Kafka] Connected to {BOOTSTRAP}, subscribed to {TOPIC}')
        
        for msg in consumer:
            await handler(msg.value)
            await asyncio.sleep(0)  # Yield to event loop
            
    except Exception as e:
        print(f'[Kafka Error] {e}')