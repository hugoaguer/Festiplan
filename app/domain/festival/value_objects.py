
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(
                "La date de fin doit Ãªtre postÃ©rieure Ã  la date de dÃ©but"
            )

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.start < other.end and self.end > other.start


@dataclass(frozen=True)
class FestivalPeriod:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(
                "La date de fin doit Ãªtre postÃ©rieure Ã  la date de dÃ©but"
            )

    def contains(self, slot: TimeSlot) -> bool:
        return self.start <= slot.start and slot.end <= self.end


@dataclass(frozen=True)
class EquipmentSet:
    items: frozenset[str]

    @classmethod
    def from_string(cls, equipment: str | None) -> "EquipmentSet":
        return cls(
            frozenset(
                item.strip()
                for item in (equipment or "").split(",")
                if item.strip()
            )
        )

    def supports(self, required: "EquipmentSet") -> bool:
        return required.items.issubset(self.items)
