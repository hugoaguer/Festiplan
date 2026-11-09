
from dataclasses import dataclass
from datetime import datetime

from app.domain.festival.value_objects import (
    EquipmentSet,
    FestivalPeriod,
    TimeSlot,
)


@dataclass
class Festival:
    id: int | None
    name: str
    location: str
    start_date: datetime
    end_date: datetime
    status: str = "preparation"

    @property
    def period(self) -> FestivalPeriod:
        return FestivalPeriod(self.start_date, self.end_date)

    def ensure_editable(self) -> None:
        if self.status == "published":
            raise ValueError(
                "Impossible de modifier le planning : "
                "le planning est dÃ©jÃ  publiÃ©"
            )

    def publish(self) -> None:
        self.ensure_editable()
        self.status = "published"


@dataclass
class Stage:
    id: int | None
    festival_id: int
    name: str
    capacity: int
    available_equipment: str = ""

    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError(
                "La capacitÃ© de la scÃ¨ne doit Ãªtre positive"
            )

    def supports(self, required_equipment: str) -> bool:
        available = EquipmentSet.from_string(
            self.available_equipment
        )
        required = EquipmentSet.from_string(
            required_equipment
        )

        return available.supports(required)


@dataclass
class Concert:
    id: int | None
    festival_id: int
    artist_id: int
    stage_id: int
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"

    def __post_init__(self):
        TimeSlot(self.start_time, self.end_time)

    @property
    def time_slot(self) -> TimeSlot:
        return TimeSlot(self.start_time, self.end_time)

    def reschedule(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> None:
        if self.status == "cancelled":
            raise ValueError(
                "Impossible de dÃ©placer un concert annulÃ©"
            )

        TimeSlot(start_time, end_time)

        self.start_time = start_time
        self.end_time = end_time

    def cancel(self) -> None:
        if self.status == "cancelled":
            raise ValueError(
                "Le concert est dÃ©jÃ  annulÃ©"
            )

        self.status = "cancelled"
