from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
from .health import get_database_size, check_database_connection, get_active_connections, get_long_running_queries
import httpx, asyncio, time

app = APIRouter()

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class MonitorPayLoad(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]


async def monitor_task(payload: MonitorPayLoad):
    """Background task to monitor database and send results."""
    results = await asyncio.gather(
        check_database_connection(payload),
        get_database_size(payload),
        get_active_connections(payload),
        get_long_running_queries(payload)
    )
    results_text = "\n".join(results)
    telex_format = {
        "message": results_text,
        "username": "DB Monitor",
        "event_name": "Database Check",
        "status": "error" if "Error" in results_text else "success"
    }
    async with httpx.AsyncClient() as client:
        await client.post(payload.return_url, json=telex_format, headers={"Content-Type": "application/json"})

# @app.post("/monitor")
# def start_monitoring(payload: MonitorPayload, background_tasks: BackgroundTasks):
#     background_tasks.add_task(monitor_task, payload)
#     return {"message": "Monitoring started", "sites": [s.default for s in payload.settings if s.label.startswith("site")]}
