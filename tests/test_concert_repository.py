
from datetime import datetime

from app.domain.concert import Concert as DomainConcert
from app.adapters.outbound.persistence.sqlalchemy.models import Concert as ConcertModel
from app.adapters.outbound.persistence.sqlalchemy.repositories.concert_repository import ConcertRepository

# RÃ©utiliser les fixtures du fichier de rÃ©gression
from tests.test_regression import db, festival_data  # noqa: F401


def test_repository_get(db, festival_data):
    repository = ConcertRepository(db)

    concert = repository.get(festival_data["concert1_id"])

    assert concert is not None
    assert isinstance(concert, DomainConcert)
    assert concert.id == festival_data["concert1_id"]


def test_repository_list(db, festival_data):
    repository = ConcertRepository(db)

    concerts = repository.list_for_festival(
        festival_data["festival_id"]
    )

    assert len(concerts) == 2
    assert all(isinstance(c, DomainConcert) for c in concerts)


def test_repository_create(db, festival_data):
    repository = ConcertRepository(db)

    concert = DomainConcert(
        id=None,
        festival_id=festival_data["festival_id"],
        artist_id=festival_data["artist_id"],
        stage_id=festival_data["stage_id"],
        start_time=datetime(2026, 7, 10, 18),
        end_time=datetime(2026, 7, 10, 19)
    )

    created = repository.create(concert)

    assert created.id is not None
    assert isinstance(created, DomainConcert)

    saved = db.get(ConcertModel, created.id)

    assert saved is not None
    assert saved.start_time.hour == 18


def test_repository_save(db, festival_data):
    repository = ConcertRepository(db)

    concert = repository.get(festival_data["concert1_id"])

    concert.reschedule(
        datetime(2026, 7, 10, 18),
        datetime(2026, 7, 10, 19)
    )

    saved = repository.save(concert)

    assert isinstance(saved, DomainConcert)
    assert saved.start_time.hour == 18

    db.expire_all()

    model = db.get(ConcertModel, concert.id)

    assert model.start_time.hour == 18


def test_repository_get_unknown_concert(db, festival_data):
    repository = ConcertRepository(db)

    concert = repository.get(999999)

    assert concert is None
