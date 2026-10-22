
from datetime import datetime
from unittest.mock import patch

import pytest

from app.database import SessionLocal
from app.models import Festival, Artist, Stage, Concert
from app.services.scheduling_service import SchedulingService
from app.services.publication_service import PublicationService
from app.schemas import ConcertReschedule


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
        status="preparation"
    )

    artist1 = Artist(
        name="Groupe Metal A",
        genre="Metal",
        required_equipment="guitare,batterie"
    )

    artist2 = Artist(
        name="Groupe Metal B",
        genre="Metal",
        required_equipment="guitare"
    )

    db.add_all([festival, artist1, artist2])
    db.flush()

    stage1 = Stage(
        festival_id=festival.id,
        name="Main Stage",
        capacity=5000,
        available_equipment="guitare,batterie"
    )

    stage2 = Stage(
        festival_id=festival.id,
        name="Second Stage",
        capacity=2000,
        available_equipment="guitare,batterie"
    )

    db.add_all([stage1, stage2])
    db.flush()

    concert1 = Concert(
        festival_id=festival.id,
        artist_id=artist1.id,
        stage_id=stage1.id,
        start_time=datetime(2026, 7, 10, 14),
        end_time=datetime(2026, 7, 10, 15)
    )

    concert2 = Concert(
        festival_id=festival.id,
        artist_id=artist2.id,
        stage_id=stage1.id,
        start_time=datetime(2026, 7, 10, 16),
        end_time=datetime(2026, 7, 10, 17)
    )

    db.add_all([concert1, concert2])
    db.commit()

    return {
        "festival_id": festival.id,
        "artist_id": artist1.id,
        "stage_id": stage2.id,
        "concert1_id": concert1.id,
        "concert2_id": concert2.id
    }


def test_concert_overlap_is_rejected(db, festival_data):
    service = SchedulingService(db)

    payload = ConcertReschedule(
        start_time=datetime(2026, 7, 10, 14, 30),
        end_time=datetime(2026, 7, 10, 15, 30)
    )

    with pytest.raises(ValueError, match="scène"):
        service.reschedule_concert(
            festival_data["concert2_id"], payload
        )

    db.expire_all()
    concert = db.get(Concert, festival_data["concert2_id"])

    assert concert.start_time == datetime(2026, 7, 10, 16)


def test_notification_failure_does_not_cancel_change(db, festival_data):
    service = SchedulingService(db)

    payload = ConcertReschedule(
        start_time=datetime(2026, 7, 10, 18),
        end_time=datetime(2026, 7, 10, 19)
    )

    with patch.object(
        service.notifications,
        "notify_schedule_change",
        side_effect=RuntimeError("Notification indisponible")
    ):
        concert = service.reschedule_concert(
            festival_data["concert2_id"], payload
        )

    assert concert.start_time == datetime(2026, 7, 10, 18)

    db.expire_all()
    saved = db.get(Concert, festival_data["concert2_id"])

    assert saved.start_time == datetime(2026, 7, 10, 18)


def test_published_schedule_cannot_be_modified(db, festival_data):
    publication = PublicationService(db)

    with patch.object(
        publication.notifications,
        "notify_schedule_change"
    ):
        publication.publish(festival_data["festival_id"])

    service = SchedulingService(db)

    payload = ConcertReschedule(
        start_time=datetime(2026, 7, 10, 18),
        end_time=datetime(2026, 7, 10, 19)
    )

    with pytest.raises(ValueError, match="publié"):
        service.reschedule_concert(
            festival_data["concert2_id"], payload
        )

    db.expire_all()
    concert = db.get(Concert, festival_data["concert2_id"])

    assert concert.start_time == datetime(2026, 7, 10, 16)
