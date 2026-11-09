
from dataclasses import dataclass
from datetime import datetime

from app.domain.concert_rules import validate_concert_dates


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
        validate_concert_dates(
            self.start_time,
            self.end_time
        )

    def reschedule(
        self,
        start_time: datetime,
        end_time: datetime
    ):
        if self.status == "cancelled":
            raise ValueError(
                "Impossible de dÃ©placer un concert annulÃ©"
            )

        validate_concert_dates(start_time, end_time)

        self.start_time = start_time
        self.end_time = end_time

    def cancel(self):
        if self.status == "cancelled":
            raise ValueError(
                "Le concert est dÃ©jÃ  annulÃ©"
            )

        self.status = "cancelled"
