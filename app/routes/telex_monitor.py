from pydantic import BaseModel
from typing import List,Dict
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

async def check_site_status(site: str) -> Dict[str, str]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(site, timeout=10)
            return {"site": site, "status_code": response.status_code, "response": response.text}
    except Exception as e:
        return {"site": site, "error": str(e)}


async def monitor_task(payload: MonitorPayload):
    sites = [s.default for s in payload.settings if s.label.startswith("site")]
    results = await asyncio.gather(*(check_site_status(site) for site in sites))

    message = "\n".join([result for result in results if result is not None])

    # data follows telex webhook format. Your integration must call the return_url using this format
    data = {
        "message": message,
        "username": "Postgres Monitor",
        "event_name": "status Check",
        "status": check_site_status().response
    }

    async with httpx.AsyncClient() as client:
        await client.post(payload.return_url, json=data)


