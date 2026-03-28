import redis.asyncio as aioredis
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Connects to your otdt-redis container
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
_client = None

async def get_redis():
    global _client
    if _client is None:
        _client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _client

async def set_asset_state(asset_id: str, state: dict, ttl: int = 60):
    """Caches the complete asset state (sensors + AI scores) for quick lookup."""
    r = await get_redis()
    await r.setex(f'asset:{asset_id}', ttl, json.dumps(state))

async def get_asset_state(asset_id: str) -> dict | None:
    """Retrieves a single asset state."""
    r = await get_redis()
    v = await r.get(f'asset:{asset_id}')
    return json.loads(v) if v else None

async def get_all_asset_states() -> list:
    """Retrieves all 50 asset states for the dashboard overview."""
    r = await get_redis()
    keys = await r.keys('asset:*')
    if not keys: 
        return []
    vals = await r.mget(*keys)
    return [json.loads(v) for v in vals if v]