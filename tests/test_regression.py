
from datetime import datetime
from unittest.mock import Mock

import pytest

from app.adapters.outbound.persistence.sqlalchemy.database import SessionLocal
from app.adapters.outbound.persistence.sqlalchemy.models import (
    Festival,
    Artist,
    Stage,
    Concert,
)

from app.adapters.outbound.persistence.sqlalchemy.repositories.artist_repository import (
    ArtistRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.concert_repository import (
    ConcertRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.festival_repository import (
    FestivalRepository,
)
from app.adapters.outbound.persistence.sqlalchemy.repositories.stage_repository import (
    StageRepository,
)

from app.application.use_cases.reschedule_concert import (
    RescheduleConcertUseCase,
)
from app.application.use_cases.publish_festival import (
    PublishFestivalUseCase,
)


@pytest.fixture
def db(client):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def festival_data(db):
    festival = Festival(
        name="FestiPlan Test",
        location="Bordeaux",
        start_date=datetime(2026, 7, 10, 10),
        end_date=datetime(2026, 7, 12, 23),
        status="preparation",
    )

    artist1 = Artist(
        name="Groupe Metal A",
        genre="Metal",
        required_equipment="guitare,batterie",
    )

    artist2 = Artist(
        name="Groupe Metal B",
        genre="Metal",
        required_equipment="guitare",
    )

    db.add_all([festival, artist1, artist2])
    db.flush()

    stage1 = Stage(
        festival_id=festival.id,
        name="Main Stage",
        capacity=5000,
        available_equipment="guitare,batterie",
    )

    stage2 = Stage(
        festival_id=festival.id,
        name="Second Stage",
        capacity=2000,
        available_equipment="guitare,batterie",
    )

    db.add_all([stage1, stage2])
    db.flush()

    concert1 = Concert(
        festival_id=festival.id,
        artist_id=artist1.id,
        stage_id=stage1.id,
        start_time=datetime(2026, 7, 10, 14),
        end_time=datetime(2026, 7, 10, 15),
    )

    concert2 = Concert(
        festival_id=festival.id,
        artist_id=artist2.id,
        stage_id=stage1.id,
        start_time=datetime(2026, 7, 10, 16),
        end_time=datetime(2026, 7, 10, 17),
    )

    db.add_all([concert1, concert2])
    db.commit()

    return {
        "festival_id": festival.id,
        "artist_id": artist1.id,
        "stage_id": stage2.id,
        "concert1_id": concert1.id,
        "concert2_id": concert2.id,
    }


def make_reschedule_use_case(db, notification_sender=None):
    return RescheduleConcertUseCase(
        concert_repo=ConcertRepository(db),
        festival_repo=FestivalRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notification_sender=notification_sender,
    )


def test_concert_overlap_is_rejected(db, festival_data):
    use_case = make_reschedule_use_case(db)

    with pytest.raises(ValueError, match="scène"):
        use_case.execute(
            concert_id=festival_data["concert2_id"],
            start_time=datetime(2026, 7, 10, 14, 30),
            end_time=datetime(2026, 7, 10, 15, 30),
        )

    db.expire_all()

    concert = db.get(
        Concert,
        festival_data["concert2_id"],
    )

    assert concert.start_time == datetime(2026, 7, 10, 16)


def test_notification_failure_does_not_cancel_change(db, festival_data):
    notification_sender = Mock()
    notification_sender.notify_schedule_change.side_effect = RuntimeError(
        "Notification indisponible"
    )

    use_case = make_reschedule_use_case(
        db,
        notification_sender=notification_sender,
    )

    concert = use_case.execute(
        concert_id=festival_data["concert2_id"],
        start_time=datetime(2026, 7, 10, 18),
        end_time=datetime(2026, 7, 10, 19),
    )

    assert concert.start_time == datetime(2026, 7, 10, 18)

    notification_sender.notify_schedule_change.assert_called_once()

    db.expire_all()

    saved = db.get(
        Concert,
        festival_data["concert2_id"],
    )

    assert saved.start_time == datetime(2026, 7, 10, 18)


def test_published_schedule_cannot_be_modified(db, festival_data):
    notification_sender = Mock()

    publication = PublishFestivalUseCase(
        festival_repo=FestivalRepository(db),
        concert_repo=ConcertRepository(db),
        artist_repo=ArtistRepository(db),
        stage_repo=StageRepository(db),
        notification_sender=notification_sender,
    )

    published_festival = publication.execute(
        festival_data["festival_id"]
    )

    assert published_festival.status == "published"

    use_case = make_reschedule_use_case(db)

    with pytest.raises(ValueError, match="publié"):
        use_case.execute(
            concert_id=festival_data["concert2_id"],
            start_time=datetime(2026, 7, 10, 18),
            end_time=datetime(2026, 7, 10, 19),
        )

    db.expire_all()

    concert = db.get(
        Concert,
        festival_data["concert2_id"],
    )

    assert concert.start_time == datetime(2026, 7, 10, 16)
