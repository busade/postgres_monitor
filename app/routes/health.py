from fastapi import APIRouter, HTTPException
from app.db.postgres import engine,check_postgres
import asyncio
from sqlalchemy import text


router = APIRouter()

@router.get('/health/postgres')
async def postgres_health():
    return await check_postgres()

@router.get('/health')
async def full_health_check():
    db_status = await check_postgres()
    if db_status["status"]== "error":
        return {"status":" ERROR", "message":db_status["details"]},500
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
        return {"status":"OK", "database_version":version}
    except Exception as e:
        return{"status":"ERROR", "message":str(e)},500



@router.get("/database_size")
async def get_database_size():
    """Retrieves size of database"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()));"))
            size = result.scalar()
            return {"size":size}
    except Exception as e:
        return {"status":"ERROR", "message":str(e)},500
    

@router.get("/active_connections")
async def get_active_connections():
    """Retrieves all active connections"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) from pg_stat_activity"))
            active_connections = result.scalar()
            return {"Number of active Connections":active_connections}
    except Exception as e:
        return {"status":"ERROR","message":str(e)},500
    
@router.get("/long_running_queries")
async def get_long_running_queries(threshold: int=10):
    """Retrieves queries longer than the specified threshold"""
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
            queries =  []
            for q_info in long_queries:
                queries.append({
                    "pid":q_info[0],
                    "state": q_info[1],
                    "query":q_info[2],
                    "duration": q_info[3]
                })
            return{"long_running_queries":queries}
    except Exception as e:
        return {"status":"ERROR","message":str(e)},500
