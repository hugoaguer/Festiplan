
from datetime import datetime

from app.domain.concert import Concert as DomainConcert
from app.adapters.outbound.persistence.sqlalchemy.mappings import (
    to_domain,
    to_model,
    update_model,
)


def create_domain_concert():
    return DomainConcert(
        id=1,
        festival_id=1,
        artist_id=2,
        stage_id=3,
        start_time=datetime(2026, 7, 10, 14),
        end_time=datetime(2026, 7, 10, 15)
    )


def test_domain_to_model():
    concert = create_domain_concert()

    model = to_model(concert)

    assert model.id == 1
    assert model.artist_id == 2
    assert model.stage_id == 3


def test_model_to_domain():
    concert = create_domain_concert()
    model = to_model(concert)

    result = to_domain(model)

    assert isinstance(result, DomainConcert)
    assert result.start_time == concert.start_time
    assert result.status == "scheduled"


def test_update_model():
    concert = create_domain_concert()
    model = to_model(concert)

    concert.reschedule(
        datetime(2026, 7, 10, 16),
        datetime(2026, 7, 10, 17)
    )

    update_model(model, concert)

    assert model.start_time.hour == 16
    assert model.end_time.hour == 17
