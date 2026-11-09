
from fastapi import Depends
from sqlalchemy.orm import Session

# ==========================================
# DATABASE
# ==========================================

from app.adapters.outbound.persistence.sqlalchemy.database import get_db

# ==========================================
# REPOSITORIES
# ==========================================

from app.adapters.outbound.persistence.sqlalchemy.repositories.concert_repository import (
    ConcertRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.festival_repository import (
    FestivalRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.artist_repository import (
    ArtistRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.stage_repository import (
    StageRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.incident_repository import (
    IncidentRepository,
)

# ==========================================
# NOTIFICATIONS
# ==========================================

from app.adapters.outbound.notifications.email_sender import (
    EmailNotificationSender,
)

# ==========================================
# USE CASES
# ==========================================

from app.application.use_cases.create_concert import (
    CreateConcertUseCase,
)
from app.application.use_cases.reschedule_concert import (
    RescheduleConcertUseCase,
)
from app.application.use_cases.cancel_concert import (
    CancelConcertUseCase,
)
from app.application.use_cases.create_festival import (
    CreateFestivalUseCase,
)
from app.application.use_cases.publish_festival import (
    PublishFestivalUseCase,
)
from app.application.use_cases.create_artist import (
    CreateArtistUseCase,
)
from app.application.use_cases.create_stage import (
    CreateStageUseCase,
)
from app.application.use_cases.report_incident import (
    ReportIncidentUseCase,
)

# ==========================================
# QUERIES
# ==========================================

from app.application.queries.get_concert import (
    GetConcertQuery,
)
from app.application.queries.list_concerts import (
    ListConcertsQuery,
)
from app.application.queries.list_festivals import (
    ListFestivalsQuery,
)
from app.application.queries.list_artists import (
    ListArtistsQuery,
)
from app.application.queries.list_stages import (
    ListStagesQuery,
)
from app.application.queries.list_incidents import (
    ListIncidentsQuery,
)


# ==========================================
# CONCERT USE CASES
# ==========================================

def get_create_concert_use_case(
    db: Session = Depends(get_db),
) -> CreateConcertUseCase:
    return CreateConcertUseCase(
        concert_repo=ConcertRepository(db),
        festival_repo=FestivalRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
    )


def get_reschedule_concert_use_case(
    db: Session = Depends(get_db),
) -> RescheduleConcertUseCase:
    return RescheduleConcertUseCase(
        concert_repo=ConcertRepository(db),
        festival_repo=FestivalRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notification_sender=EmailNotificationSender(),
    )


def get_cancel_concert_use_case(
    db: Session = Depends(get_db),
) -> CancelConcertUseCase:
    return CancelConcertUseCase(
        concert_repo=ConcertRepository(db),
        festival_repo=FestivalRepository(db),
    )


# ==========================================
# CONCERT QUERIES
# ==========================================

def get_concert_query(
    db: Session = Depends(get_db),
) -> GetConcertQuery:
    return GetConcertQuery(
        concert_repo=ConcertRepository(db),
    )


def get_list_concerts_query(
    db: Session = Depends(get_db),
) -> ListConcertsQuery:
    return ListConcertsQuery(
        concert_repo=ConcertRepository(db),
    )


# ==========================================
# FESTIVAL USE CASES
# ==========================================

def get_create_festival_use_case(
    db: Session = Depends(get_db),
) -> CreateFestivalUseCase:
    return CreateFestivalUseCase(
        festival_repo=FestivalRepository(db),
    )


def get_publish_festival_use_case(
    db: Session = Depends(get_db),
) -> PublishFestivalUseCase:
    return PublishFestivalUseCase(
        festival_repo=FestivalRepository(db),
        concert_repo=ConcertRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notification_sender=EmailNotificationSender(),
    )


# ==========================================
# FESTIVAL QUERIES
# ==========================================

def get_list_festivals_query(
    db: Session = Depends(get_db),
) -> ListFestivalsQuery:
    return ListFestivalsQuery(
        festival_repo=FestivalRepository(db),
    )


# ==========================================
# ARTIST USE CASES
# ==========================================

def get_create_artist_use_case(
    db: Session = Depends(get_db),
) -> CreateArtistUseCase:
    return CreateArtistUseCase(
        artist_repo=ArtistRepository(db),
    )


# ==========================================
# ARTIST QUERIES
# ==========================================

def get_list_artists_query(
    db: Session = Depends(get_db),
) -> ListArtistsQuery:
    return ListArtistsQuery(
        artist_repo=ArtistRepository(db),
    )


# ==========================================
# STAGE USE CASES
# ==========================================

def get_create_stage_use_case(
    db: Session = Depends(get_db),
) -> CreateStageUseCase:
    return CreateStageUseCase(
        stage_repo=StageRepository(db),
        festival_repo=FestivalRepository(db),
    )


# ==========================================
# STAGE QUERIES
# ==========================================

def get_list_stages_query(
    db: Session = Depends(get_db),
) -> ListStagesQuery:
    return ListStagesQuery(
        stage_repo=StageRepository(db),
    )


# ==========================================
# INCIDENT USE CASES
# ==========================================

def get_report_incident_use_case(
    db: Session = Depends(get_db),
) -> ReportIncidentUseCase:
    return ReportIncidentUseCase(
        incident_repo=IncidentRepository(db),
        concert_repo=ConcertRepository(db),
    )


# ==========================================
# INCIDENT QUERIES
# ==========================================

def get_list_incidents_query(
    db: Session = Depends(get_db),
) -> ListIncidentsQuery:
    return ListIncidentsQuery(
        incident_repo=IncidentRepository(db),
    )
