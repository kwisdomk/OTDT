import asyncio
import json
import os
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('KAFKA_TOPIC_SENSORS', 'ot-twin-sensors')

async def consume(handler):
    """
    Async Kafka consumer that hands off messages to the handle_telemetry function.
    """
    try:
        # Use kafka-python (matching your pip install)
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP,
            value_deserializer=lambda b: json.loads(b.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='otDT-api-group'
        )
        print(f'[Kafka] Connected to {BOOTSTRAP}, subscribed to {TOPIC}')
        
        # We wrap the blocking consumer in an async-friendly way
        for msg in consumer:
            await handler(msg.value)
            await asyncio.sleep(0)  # Let the event loop breathe
            
    except Exception as e:
        print(f'[Kafka Error] {e}')
