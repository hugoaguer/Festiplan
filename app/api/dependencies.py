
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.repositories.concert_repository import ConcertRepository
from app.repositories.festival_repository import FestivalRepository
from app.repositories.artist_repository import ArtistRepository
from app.repositories.stage_repository import StageRepository
from app.repositories.incident_repository import IncidentRepository

from app.services.scheduling_service import SchedulingService
from app.services.festival_service import FestivalService
from app.services.publication_service import PublicationService
from app.services.artist_service import ArtistService
from app.services.stage_service import StageService
from app.services.incident_service import IncidentService
from app.services.notification_service import NotificationService


def get_scheduling_service(
    db: Session = Depends(get_db),
) -> SchedulingService:
    return SchedulingService(
        db=db,
        repo=ConcertRepository(db),
        festival_repo=FestivalRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notifications=NotificationService(),
    )


def get_festival_service(
    db: Session = Depends(get_db),
) -> FestivalService:
    return FestivalService(
        db=db,
        repo=FestivalRepository(db),
    )


def get_publication_service(
    db: Session = Depends(get_db),
) -> PublicationService:
    return PublicationService(
        festival_repo=FestivalRepository(db),
        concert_repo=ConcertRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notifications=NotificationService(),
    )


def get_artist_service(
    db: Session = Depends(get_db),
) -> ArtistService:
    return ArtistService(
        repo=ArtistRepository(db),
    )


def get_stage_service(
    db: Session = Depends(get_db),
) -> StageService:
    return StageService(
        stage_repo=StageRepository(db),
        festival_repo=FestivalRepository(db),
    )


def get_incident_service(
    db: Session = Depends(get_db),
) -> IncidentService:
    return IncidentService(
        incident_repo=IncidentRepository(db),
        concert_repo=ConcertRepository(db),
    )
