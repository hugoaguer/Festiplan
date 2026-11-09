
from datetime import datetime

import pytest

from app.domain.concert_rules import (
    validate_concert_dates,
    check_concert_overlap,
    validate_stage_equipment,
)


def test_valid_concert_dates():
    start = datetime(2026, 7, 10, 14, 0)
    end = datetime(2026, 7, 10, 15, 0)

    validate_concert_dates(start, end)


def test_invalid_concert_dates():
    start = datetime(2026, 7, 10, 15, 0)
    end = datetime(2026, 7, 10, 14, 0)

    with pytest.raises(ValueError):
        validate_concert_dates(start, end)


def test_concert_overlap():
    start = datetime(2026, 7, 10, 14, 0)
    end = datetime(2026, 7, 10, 16, 0)

    other_start = datetime(2026, 7, 10, 15, 0)
    other_end = datetime(2026, 7, 10, 17, 0)

    assert check_concert_overlap(
        start, end, other_start, other_end
    ) is True


def test_concert_without_overlap():
    start = datetime(2026, 7, 10, 14, 0)
    end = datetime(2026, 7, 10, 15, 0)

    other_start = datetime(2026, 7, 10, 15, 0)
    other_end = datetime(2026, 7, 10, 16, 0)

    assert check_concert_overlap(
        start, end, other_start, other_end
    ) is False


def test_invalid_stage_equipment():
    with pytest.raises(ValueError):
        validate_stage_equipment(
            "guitare,batterie",
            "guitare,micro"
        )
