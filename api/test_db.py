# api/test_db.py
import asyncio
from db.timescale import init_schema, get_pool

async def test_connection():
    print("--- OTDT Database Connection Test ---")
    try:
        # 1. Test raw connection
        pool = await get_pool()
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version();")
            print(f"[SUCCESS] Connected to: {version}")
            
            # 2. Run your schema initialisation logic
            await init_schema()
            
            # 3. Verify tables and hypertables
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            print(f"[SUCCESS] Tables in DB: {[t['table_name'] for t in tables]}")
            
            # Check for TimescaleDB hypertable specifically
            is_hyper = await conn.fetchval("""
                SELECT count(*) FROM _timescaledb_catalog.hypertable 
                WHERE table_name = 'sensor_readings';
            """)
            if is_hyper:
                print("[SUCCESS] 'sensor_readings' is a verified Hypertable.")
            
    except Exception as e:
        print(f"[FAILED] Database test failed: {e}")
    finally:
        print("--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(test_connection())
