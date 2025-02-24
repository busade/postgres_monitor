from fastapi import APIRouter,Request,BackgroundTasks
from fastapi.responses import JSONResponse
from .telex_monitor import MonitorPayLoad,monitor_task


app = APIRouter()
  
json_integration={
  "data": {
    "date": {
      "created_at": "2025-02-18",
      "updated_at": "2025-02-18"
    },
    "descriptions": {
      "app_name": "Postgresql Database Performance ",
      "app_description": "Postgres Database Monitoring system",
      "app_logo": "https://postgres-monitor.onrender.com",
      "app_url": "https://postgres-monitor.onrender.com",
      "background_color": "#fff"
    },
    "is_active": True,
    "integration_type": "interval",
    "key_features": [
      "Database Monitoring"
    ],
    "author": "Adesola",
    "integration_category": "Performance Monitoring",
    "settings": [
      {
        "label": "database",
        "type": "text",
        "required": True,
        "default": "" 
      },
     {
        "label": "Interval",
        "type": "text",
        "required": True,
        "default": "*/5 * * * *"
      }
    ],
    "target_url": "",
    "tick_url": "https://postgres-monitor.onrender.com/tick"
  }
}

@app.get("/integrated")
def get_integrated_json(request:Request):

  return JSONResponse(json_integration)


@app.post("/tick", status_code=202)
def monitor(payload: MonitorPayLoad, background_tasks: BackgroundTasks):
    background_tasks.add_task(monitor_task, payload)
    return {"status": "success"}


