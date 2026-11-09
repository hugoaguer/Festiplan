
from datetime import datetime

import pytest

from app.domain.concert import Concert


def create_concert():
    return Concert(
        id=1,
        festival_id=1,
        artist_id=1,
        stage_id=1,
        start_time=datetime(2026, 7, 10, 14),
        end_time=datetime(2026, 7, 10, 15)
    )


def test_create_concert():
    concert = create_concert()

    assert concert.status == "scheduled"
    assert concert.id == 1


def test_reschedule_concert():
    concert = create_concert()

    concert.reschedule(
        datetime(2026, 7, 10, 16),
        datetime(2026, 7, 10, 17)
    )

    assert concert.start_time.hour == 16
    assert concert.end_time.hour == 17


def test_invalid_reschedule():
    concert = create_concert()

    with pytest.raises(ValueError):
        concert.reschedule(
            datetime(2026, 7, 10, 17),
            datetime(2026, 7, 10, 16)
        )


def test_cancel_concert():
    concert = create_concert()

    concert.cancel()

    assert concert.status == "cancelled"


def test_cancel_twice():
    concert = create_concert()
    concert.cancel()

    with pytest.raises(ValueError):
        concert.cancel()


def test_reschedule_cancelled_concert():
    concert = create_concert()
    concert.cancel()

    with pytest.raises(ValueError):
        concert.reschedule(
            datetime(2026, 7, 10, 16),
            datetime(2026, 7, 10, 17)
        )
