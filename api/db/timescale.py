# api/db/timescale.py
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Connects to the local Docker container or OCP service
DB_URL = os.getenv('TIMESCALEDB_URL', 'postgresql://postgres:password@localhost:5432/otdt')
_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    return _pool

async def init_schema():
    """Initialises the TimescaleDB schema with hypertables for sensor data."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Create standard table for sensor readings
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                time        TIMESTAMPTZ NOT NULL,
                asset_id    TEXT        NOT NULL,
                sensor_name TEXT        NOT NULL,
                value       DOUBLE PRECISION NOT NULL
            );
        ''')
        # Convert to TimescaleDB hypertable for time-series optimisation
        await conn.execute('''
            SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE);
        ''')
        # Index for fast lookups by asset and time
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_sensor_asset_time
            ON sensor_readings (asset_id, time DESC);
        ''')
        # Table for storing Monte Carlo simulation results
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS mc_results (
                time                    TIMESTAMPTZ PRIMARY KEY DEFAULT now(),
                asset_id                TEXT    NOT NULL,
                failure_probability     FLOAT   NOT NULL,
                days_to_failure_p50     INT,
                recommended_action      TEXT,
                optimal_maintenance_day DATE
            );
        ''')
    print('[DB] TimescaleDB Schema ready')

async def store_reading(asset_id: str, sensors: dict, ts: str):
    """Persists a batch of sensor readings to the hypertable."""
    from datetime import datetime
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Convert string timestamp to datetime
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        rows = [(dt, asset_id, k, v) for k, v in sensors.items() if v is not None]
        await conn.executemany(
            'INSERT INTO sensor_readings (time, asset_id, sensor_name, value) VALUES ($1, $2, $3, $4)',
            rows,
        )

async def latest_readings(asset_id: str) -> dict:
    """Retrieves the most recent reading for every sensor of a specific asset."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT DISTINCT ON (sensor_name) sensor_name, value, time
            FROM sensor_readings WHERE asset_id=$1
            ORDER BY sensor_name, time DESC
        ''', asset_id)
        return {r['sensor_name']: r['value'] for r in rows}