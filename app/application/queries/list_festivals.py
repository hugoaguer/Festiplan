
from app.application.ports.outbound.festival_repository_port import (
    FestivalRepositoryPort,
)


class ListFestivalsQuery:
    def __init__(self, festival_repo: FestivalRepositoryPort):
        self.festival_repo = festival_repo

    def execute(self):
        return self.festival_repo.list()
