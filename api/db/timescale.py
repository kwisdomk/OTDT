"""
TimescaleDB integration for OT Digital Twin.
Mock mode enabled when no DATABASE_URL is set.
"""

import os
import asyncpg
from typing import Optional

_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> Optional[asyncpg.Pool]:
    """Return database connection pool or None if not configured."""
    global _pool
    if _pool:
        return _pool
    
    db_url = os.getenv("TIMESCALEDB_URL", "")
    if not db_url:
        print("[DB] No TIMESCALEDB_URL set — running in mock mode")
        return None
    
    try:
        _pool = await asyncpg.create_pool(db_url, min_size=1, max_size=10)
        print("[DB] Connected to TimescaleDB")
        return _pool
    except Exception as e:
        print(f"[DB] Connection failed: {e} — running in mock mode")
        return None

async def init_schema() -> None:
    """Initialize TimescaleDB schema if database is available."""
    pool = await get_pool()
    if not pool:
        print("[DB] Mock mode — skipping schema initialization")
        return
    
    async with pool.acquire() as conn:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb;')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                time TIMESTAMPTZ NOT NULL,
                asset_id TEXT NOT NULL,
                sensor_name TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                synthetic BOOLEAN DEFAULT TRUE
            );
        ''')
        await conn.execute(
            "SELECT create_hypertable('sensor_readings','time',if_not_exists=>TRUE);"
        )
        print("[DB] Schema initialized")

async def store_reading(asset_id: str, sensors: dict, ts: str) -> None:
    """Store sensor reading if database available."""
    pool = await get_pool()
    if not pool:
        return  # Mock mode — silently ignore
    
    async with pool.acquire() as conn:
        rows = [(ts, asset_id, k, v, True) for k, v in sensors.items() if v is not None]
        if rows:
            await conn.executemany(
                'INSERT INTO sensor_readings(time,asset_id,sensor_name,value,synthetic) VALUES($1,$2,$3,$4,$5)',
                rows
            )

async def latest_readings(asset_id: str) -> dict:
    """Get latest readings if database available."""
    pool = await get_pool()
    if not pool:
        # Return mock data for demo
        return {
            "temperature_c": 85.3,
            "pressure_bar": 46.2,
            "vibration_mm_s": 2.1,
            "flow_rate_kg_s": 125.4,
            "rotation_rpm": 3580
        }
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''SELECT DISTINCT ON (sensor_name) sensor_name, value
               FROM sensor_readings WHERE asset_id=$1
               ORDER BY sensor_name, time DESC''',
            asset_id
        )
        return {r['sensor_name']: r['value'] for r in rows}

# Made with Bob
