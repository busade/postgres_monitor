from pydantic import BaseModel
from typing import List
from fastapi import BackgroundTasks
import httpx
import asyncio

class Setting(BaseModel):
    label: str
    type: str
    required: bool
    default: str

class MonitorPayload(BaseModel):
    channel_id: str
    return_url: str
    settings: List[Setting]

async def check_site_status(site: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(site, timeout=10)
            if response.status_code < 400:
                return None
            return f"{site} is down (status {response.status_code})"
    except Exception as e:
        return f"{site} check failed: {str(e)}"

async def monitor_task(payload: MonitorPayload):
    sites = [s.default for s in payload.settings if s.label.startswith("site")]
    results = await asyncio.gather(*(check_site_status(site) for site in sites))

    message = "\n".join([result for result in results if result is not None])

    # data follows telex webhook format. Your integration must call the return_url using this format
    data = {
        "message": message,
        "username": "Uptime Monitor",
        "event_name": "Uptime Check",
        "status": "error"
    }

    async with httpx.AsyncClient() as client:
        await client.post(payload.return_url, json=data)


