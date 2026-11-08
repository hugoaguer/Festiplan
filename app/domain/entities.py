from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FestivalStatus(str, Enum):
    PREPARATION = "preparation"
    PUBLISHED = "published"


@dataclass
class Festival:
    id: int | None
    name: str
    location: str
    start_date: datetime
    end_date: datetime
    status: FestivalStatus = FestivalStatus.PREPARATION

    def __post_init__(self) -> None:
        self.status = FestivalStatus(self.status)

    def ensure_schedule_is_editable(self) -> None:
        if self.status is FestivalStatus.PUBLISHED:
            raise ValueError("Le planning publié ne peut pas être modifié")

    def publish_schedule(self) -> None:
        if self.status is not FestivalStatus.PREPARATION:
            raise ValueError("Seul un planning en préparation peut être publié")
        self.status = FestivalStatus.PUBLISHED


@dataclass
class Artist:
    id: int | None
    name: str
    genre: str
    required_equipment: str = ""


@dataclass
class Stage:
    id: int | None
    festival_id: int
    name: str
    capacity: int
    available_equipment: str = ""


@dataclass
class Concert:
    id: int | None
    festival_id: int
    artist_id: int
    stage_id: int
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"


@dataclass
class Incident:
    id: int | None
    concert_id: int
    description: str
    occurred_at: datetime | None = None
    resolved: bool = False
