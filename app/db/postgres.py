from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.event import listens_for
import asyncpg, time, os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = settings.POSTGRES_URL
engine = create_async_engine(DATABASE_URL,echo= True)

sync_engine = engine.sync_engine

@listens_for(sync_engine, "before_cursor_execute")
def before_execute(conn,cursor,statement,parameters,context,executemany):
    context._query_start_time = time.time()


@listens_for(sync_engine,"after_cursor_execute")
def after_execute(conn, cursor,statement,parameters,context,executemany):
    total_time  = time.time() - context._query_start_time
    print(f"Postgres Query executed in {total_time:.4f} seconds: {statement}")

async def check_postgres():
    """check if database is online"""
    try:
        conn = await asyncpg.connect(settings.POSTGRES_PLAIN_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error","details":str(e)}
