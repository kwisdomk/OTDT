import redis.asyncio as aioredis
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Connects to your otdt-redis container
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
_client = None
_mock_mode = False
_mock_store: dict = {}  # in-memory fallback when Redis is unreachable


async def get_redis():
    """Return Redis client, switching to mock mode on connection failure."""
    global _client, _mock_mode
    if _mock_mode:
        return None
    if _client is None:
        try:
            _client = aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
            # Ping to confirm connection is alive
            await _client.ping()
            print("[Redis] Connected to", REDIS_URL)
        except Exception as e:
            print(f"[Redis] Unavailable ({e}) — switching to in-memory mock mode")
            _client = None
            _mock_mode = True
    return _client


async def set_asset_state(asset_id: str, state: dict, ttl: int = 60):
    """Caches the complete asset state (sensors + AI scores) for quick lookup."""
    r = await get_redis()
    if r is None:  # mock mode
        _mock_store[f'asset:{asset_id}'] = json.dumps(state)
        return
    await r.setex(f'asset:{asset_id}', ttl, json.dumps(state))


async def get_asset_state(asset_id: str) -> dict | None:
    """Retrieves a single asset state."""
    r = await get_redis()
    if r is None:  # mock mode
        v = _mock_store.get(f'asset:{asset_id}')
        return json.loads(v) if v else None
    v = await r.get(f'asset:{asset_id}')
    return json.loads(v) if v else None


async def get_all_asset_states() -> list:
    """Retrieves all 50 asset states for the dashboard overview."""
    r = await get_redis()
    if r is None:  # mock mode
        return [json.loads(v) for v in _mock_store.values() if v]
    keys = await r.keys('asset:*')
    if not keys:
        return []
    vals = await r.mget(*keys)
    return [json.loads(v) for v in vals if v]