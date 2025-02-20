from fastapi import FastAPI, HTTPException
import asyncpg, asyncio,  httpx,os
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

load_dotenv()


# Database connection settings
DATABASE_URL = os.getenv("POSTGRES_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

class MonitorPayload(BaseModel):
    return_url: str

async def check_database_connection():
    """Check if the database is reachable."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        return "Database is reachable"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

async def get_database_size():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()));"))
            return f"Database size: {result.scalar()}"
    except Exception as e:
        return f"Error retrieving database size: {str(e)}"

async def get_active_connections():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity"))
            return f"Active connections: {result.scalar()}"
    except Exception as e:
        return f"Error retrieving active connections: {str(e)}"

async def get_long_running_queries(threshold: int = 10):
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f"""
                    SELECT
                        pid,
                        state,
                        query,
                        EXTRACT(EPOCH FROM (NOW()-query_start)) AS duration
                    FROM pg_stat_activity
                    WHERE state <> 'idle' and (NOW() - query_start) > INTERVAL '{threshold} seconds' 
                    ORDER BY duration DESC;
            """))
            long_queries = result.fetchall()
            queries = [f"PID: {q[0]}, State: {q[1]}, Query: {q[2]}, Duration: {q[3]}s" for q in long_queries]
            return "\n".join(queries) if queries else "No long-running queries"
    except Exception as e:
        return f"Error retrieving long-running queries: {str(e)}"

