from fastapi import FastAPI, HTTPException
import asyncpg, asyncio,  httpx,os,logging
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from typing import List

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str
class MonitorPayLoad(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]


def get_db_engine(database_url: str):
    """Reusable function to get async database engine."""
    return create_async_engine(database_url, echo=True)

async def check_database_connection(payload: MonitorPayLoad):
    """Check if the database is reachable."""
    DATABASE_URL = payload.get_setting("database_url")
    engine = get_db_engine(DATABASE_URL)
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        return "Database is reachable"
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return f"Database connection failed: {str(e)}"


async def get_database_size(payload: MonitorPayLoad):
    DATABASE_URL = payload.get_setting("database_url")
    engine = get_db_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()));"))
            return f"Database size: {await result.scalar()}"
    except Exception as e:
        logger.error(f"Error retrieving database size: {str(e)}")
        return f"Error retrieving database size: {str(e)}"
    

async def get_active_connections(payload: MonitorPayLoad):
    DATABASE_URL = payload.get_setting("database_url")
    engine = get_db_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity"))
            return f"Active connections: {await result.scalar()}"
    except Exception as e:
        logger.error(f"Error retrieving active connections: {str(e)}")
        return f"Error retrieving active connections: {str(e)}"
    

async def get_long_running_queries(payload: MonitorPayLoad):
    DATABASE_URL = payload.get_setting("database_url")
    engine = get_db_engine(DATABASE_URL)
    threshold = int(payload.get_setting("max_query_duration", 10))
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f"""
                SELECT pid, state, query, EXTRACT(EPOCH FROM (NOW()-query_start)) AS duration
                FROM pg_stat_activity
                WHERE state <> 'idle' AND (NOW() - query_start) > INTERVAL '{threshold} seconds' 
                ORDER BY duration DESC;
            """))
            long_queries = await result.fetchall()
            queries = [f"PID: {q[0]}, State: {q[1]}, Query: {q[2]}, Duration: {q[3]}s" for q in long_queries]
            return "\n".join(queries) if queries else "No long-running queries"
    except Exception as e:
        logger.error(f"Error retrieving long-running queries: {str(e)}")
        return f"Error retrieving long-running queries: {str(e)}"


