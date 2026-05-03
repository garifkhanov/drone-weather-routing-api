from fastapi import FastAPI

from app.api.routers import health


app = FastAPI(
    title="Drone Weather Routing API",
    version="0.1.0",
)

app.include_router(health.router)
