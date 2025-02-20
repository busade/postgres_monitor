from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import httpx
import asyncio
import time

app = FastAPI()

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]

async def check_site_status(site: str) -> Dict[str, str]:
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(site, timeout=10)
            end_time = time.time()
            return {
                "site": site,
                "status_code": response.status_code,
                "response": response.text,
                "response_time": round(end_time - start_time, 4)
            }
    except Exception as e:
        end_time = time.time()
        return {"site": site, "error": str(e), "response_time": round(end_time - start_time, 4)}

async def monitor_task(payload: MonitorPayload):
    sites = [s.default for s in payload.settings if s.label.startswith("site")]
    results = await asyncio.gather(*(check_site_status(site) for site in sites))
    
    async with httpx.AsyncClient() as client:
        await client.post(payload.return_url, json={"results": results})

@app.post("/monitor")
def start_monitoring(payload: MonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(monitor_task, payload)
    return {"message": "Monitoring started", "sites": [s.default for s in payload.settings if s.label.startswith("site")]}
