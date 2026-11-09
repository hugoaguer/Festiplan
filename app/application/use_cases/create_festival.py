
from app.application.ports.outbound.festival_repository_port import (
    FestivalRepositoryPort,
)
from app.domain.festival.value_objects import FestivalPeriod


class CreateFestivalUseCase:
    def __init__(self, festival_repo: FestivalRepositoryPort):
        self.festival_repo = festival_repo

    def execute(
        self,
        name: str,
        location: str,
        start_date,
        end_date,
    ):
        FestivalPeriod(
            start=start_date,
            end=end_date,
        )

        data = {
            "name": name,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
        }

        return self.festival_repo.create(data)
