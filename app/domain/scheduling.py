from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


class InvalidTimeSlotError(ValueError):
    pass


class SchedulingConflictError(ValueError):
    pass


class InvalidScheduleError(ValueError):
    pass


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise InvalidTimeSlotError("La date de fin doit être postérieure à la date de début")

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class ScheduledConcert:
    concert_id: int | None
    festival_id: int
    artist_id: int
    stage_id: int
    stage_festival_id: int
    time_slot: TimeSlot
    festival_start: datetime
    festival_end: datetime
    required_equipment: frozenset[str]
    available_equipment: frozenset[str]


def equipment_set(value: str) -> frozenset[str]:
    return frozenset(item.strip() for item in value.split(",") if item.strip())


def scheduled_concert(
    concert_id: int | None,
    festival_id: int,
    artist_id: int,
    stage_id: int,
    stage_festival_id: int,
    start_time: datetime,
    end_time: datetime,
    festival_start: datetime,
    festival_end: datetime,
    required_equipment: str,
    available_equipment: str,
) -> ScheduledConcert:
    return ScheduledConcert(
        concert_id=concert_id,
        festival_id=festival_id,
        artist_id=artist_id,
        stage_id=stage_id,
        stage_festival_id=stage_festival_id,
        time_slot=TimeSlot(start_time, end_time),
        festival_start=festival_start,
        festival_end=festival_end,
        required_equipment=equipment_set(required_equipment),
        available_equipment=equipment_set(available_equipment),
    )


def validate_capacity(capacity: int) -> None:
    if capacity <= 0:
        raise ValueError("La capacité de la scène doit être strictement positive")


def validate_incident_description(description: str) -> str:
    normalized = description.strip()
    if not normalized:
        raise ValueError("La description de l'incident ne peut pas être vide")
    return normalized


def validate_concert_assignment(concert: ScheduledConcert) -> None:
    if concert.stage_festival_id != concert.festival_id:
        raise InvalidScheduleError("La scène n'appartient pas à ce festival")
    if concert.time_slot.start < concert.festival_start or concert.time_slot.end > concert.festival_end:
        raise InvalidScheduleError("Le concert doit se dérouler pendant le festival")
    if not concert.required_equipment.issubset(concert.available_equipment):
        raise InvalidScheduleError("La scène ne dispose pas de tous les équipements requis")


def validate_full_schedule(concerts: Iterable[ScheduledConcert]) -> None:
    scheduled = list(concerts)
    for index, concert in enumerate(scheduled):
        validate_concert_assignment(concert)
        ensure_no_conflicts(concert, scheduled[:index])


def ensure_no_conflicts(
    candidate: ScheduledConcert, existing: Iterable[ScheduledConcert]
) -> None:
    for concert in existing:
        if not candidate.time_slot.overlaps(concert.time_slot):
            continue
        if concert.stage_id == candidate.stage_id:
            raise SchedulingConflictError("Conflit : la scène est déjà occupée")
        if concert.artist_id == candidate.artist_id:
            raise SchedulingConflictError("Conflit : l'artiste est déjà programmé")
