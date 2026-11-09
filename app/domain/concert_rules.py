
from datetime import datetime

from app.domain.festival.value_objects import (
    TimeSlot,
    EquipmentSet,
)


def validate_concert_dates(
    start_time: datetime,
    end_time: datetime,
) -> None:
    TimeSlot(start=start_time, end=end_time)


def check_concert_overlap(
    start_time: datetime,
    end_time: datetime,
    other_start: datetime,
    other_end: datetime,
) -> bool:
    concert_slot = TimeSlot(
        start=start_time,
        end=end_time,
    )

    other_slot = TimeSlot(
        start=other_start,
        end=other_end,
    )

    return concert_slot.overlaps(other_slot)


def validate_stage_equipment(
    required_equipment: str,
    available_equipment: str,
) -> None:
    required = EquipmentSet.from_string(required_equipment)
    available = EquipmentSet.from_string(available_equipment)

    if not available.supports(required):
        raise ValueError(
            "La scÃ¨ne ne dispose pas de tous les Ã©quipements requis"
        )
