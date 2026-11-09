
from app.application.ports.outbound.concert_repository_port import (
    ConcertRepositoryPort,
)


class ListConcertsQuery:

    def __init__(self, concert_repo: ConcertRepositoryPort):
        self.concert_repo = concert_repo

    def execute(self, festival_id: int):
        return self.concert_repo.list_for_festival(festival_id)
