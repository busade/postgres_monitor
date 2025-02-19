from fastapi import FastAPI
from .routes.health import router as health_router
from .routes.integration_config import app as integration_router
from fastapi.middleware.cors import CORSMiddleware
from .core.config import Settings

app = FastAPI(title="Postgres Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(integration_router)
app.include_router(health_router,prefix="/api/v1")


@app.get('/')
def home ():
    return {"message": "Welcome FastAPI Postgres Monitoring app"}
