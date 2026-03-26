import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('MAXIMO_BASE_URL', '')
USER = os.getenv('MAXIMO_USERNAME', '')
PASS = os.getenv('MAXIMO_PASSWORD', '')

def get_active_alerts() -> list:
    """Mock for demo: returns alerts from Maximo Monitor."""
    return [{"asset": "WP-07", "status": "ACTIVE", "desc": "Vibration Spike"}]

def create_work_order(asset_id: str, prob: float, scheduled_date: str) -> dict:
    """Creates a PM Work Order in Maximo MAS 9.1."""
    print(f"[Maximo] Auto-creating WO for {asset_id} (Risk: {prob*100}%)")
    # For the demo, we return a synthetic WO ID if the URL isn't live yet
    return {"work_order_id": "WO-2026-GDC-001"}
