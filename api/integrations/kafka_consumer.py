"""
Kafka consumer for sensor telemetry.
Consumes from 'sensor.telemetry' topic and forwards to message handler.
"""
import json
import os
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
        from kafka import KafkaConsumer
        loop = asyncio.get_event_loop()

        # Run blocking KafkaConsumer constructor in thread pool
        consumer = await loop.run_in_executor(
            None,
            lambda: KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                value_deserializer=lambda b: json.loads(b.decode('utf-8')),
                auto_offset_reset='latest',
                group_id=GROUP_ID,
                enable_auto_commit=True,
                consumer_timeout_ms=1000,
            )
        )
        print(f'[Kafka] Connected to {BOOTSTRAP}, subscribed to {TOPIC}')

        while True:
            # Non-blocking poll
            messages = await loop.run_in_executor(
                None, lambda: consumer.poll(timeout_ms=100)
            )
            for tp, msgs in messages.items():
                for msg in msgs:
                    await handler(msg.value)
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f'[Kafka Error] {e} — continuing without Kafka')