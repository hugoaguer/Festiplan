from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.notifications import SimulatedNotificationAdapter
from app.adapters.sqlalchemy_repositories import (
    SQLAlchemyArtistRepository,
    SQLAlchemyConcertRepository,
    SQLAlchemyFestivalRepository,
    SQLAlchemyIncidentRepository,
    SQLAlchemyStageRepository,
)
from app.database import get_db
from app.services.artist_service import ArtistService
from app.services.festival_service import FestivalService
from app.services.incident_service import IncidentService
from app.services.publication_service import PublicationService
from app.services.scheduling_service import SchedulingService
from app.services.stage_service import StageService


def get_festival_service(db: Session = Depends(get_db)) -> FestivalService:
    return FestivalService(SQLAlchemyFestivalRepository(db))


def get_artist_service(db: Session = Depends(get_db)) -> ArtistService:
    return ArtistService(SQLAlchemyArtistRepository(db))


def get_stage_service(db: Session = Depends(get_db)) -> StageService:
    return StageService(
        SQLAlchemyStageRepository(db),
        SQLAlchemyFestivalRepository(db),
    )


def get_scheduling_service(db: Session = Depends(get_db)) -> SchedulingService:
    return SchedulingService(
        SQLAlchemyConcertRepository(db),
        SQLAlchemyFestivalRepository(db),
        SQLAlchemyArtistRepository(db),
        SQLAlchemyStageRepository(db),
        SimulatedNotificationAdapter(),
    )


def get_publication_service(db: Session = Depends(get_db)) -> PublicationService:
    return PublicationService(
        SQLAlchemyFestivalRepository(db),
        SQLAlchemyConcertRepository(db),
        SQLAlchemyArtistRepository(db),
        SQLAlchemyStageRepository(db),
        SimulatedNotificationAdapter(),
    )


def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    return IncidentService(
        SQLAlchemyConcertRepository(db),
        SQLAlchemyIncidentRepository(db),
    )
