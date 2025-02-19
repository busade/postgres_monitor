from fastapi import FastAPI,Request,BackgroundTasks
from .telex_monitor import MonitorPayload,monitor_task


app = FastAPI
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
    "settings": [
      {
        "label":"site",
        "type":"text",
        "required":True,
        "default":"https://postgres-monitor.onrender.com/api/v1"
      },

      {
        "label": "Time interval",
        "type": "dropdown",
        "required": True,
        "default": "30 sec",
        "options": [
           "30 seconds"
          "1 minute",
          "5 minutes",
          "10 minutes",
          "30 minutes",
          "45 minutes",
          "1 hour"
        ]
      }
    ],
    "target_url": "https://ping.telex.im/v1/webhooks/01951b88-2355-795a-88d6-72234ed38559",
    "tick_url": "https://postgres-monitor.onrender.com/api/v1/tick"
  }
}

@app.get("/integrated")
def get_integrated_json(request:Request):
  return json_integration


@app.post("/tick", status_code=202)
def monitor(payload: MonitorPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(monitor_task, payload)
    return {"status": "accepted"}


