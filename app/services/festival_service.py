from datetime import datetime

from app.domain.entities import Festival
from app.ports import FestivalRepository


class FestivalService:
    def __init__(self, festivals: FestivalRepository) -> None:
        self.festivals = festivals

    def list_festivals(self) -> list[Festival]:
        return list(self.festivals.list())

    def create_festival(
        self, name: str, location: str, start_date: datetime, end_date: datetime
    ) -> Festival:
        if end_date <= start_date:
            raise ValueError("La date de fin doit être postérieure à la date de début")
        return self.festivals.create(
            Festival(None, name, location, start_date, end_date)
        )
