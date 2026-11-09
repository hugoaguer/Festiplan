
from fastapi import FastAPI

from app.bootstrap.config import settings
from app.adapters.outbound.persistence.sqlalchemy.database import Base, engine
from app.adapters.outbound.persistence.sqlalchemy import models  # noqa: F401

from app.adapters.inbound.web.routes import (
    festivals,
    artists,
    stages,
    concerts,
    incidents,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de gestion d'un festival fictif",
)

for router in (
    festivals.router,
    artists.router,
    stages.router,
    concerts.router,
    incidents.router,
):
    app.include_router(router)


@app.get("/")
def health():
    return {
        "message": "Bienvenue sur FestiPlan",
        "status": "ok",
    }
