
from app.application.ports.outbound.concert_repository_port import (
    ConcertRepositoryPort,
)


class GetConcertQuery:

    def __init__(self, concert_repo: ConcertRepositoryPort):
        self.concert_repo = concert_repo

    def execute(self, concert_id: int):
        return self.concert_repo.get(concert_id)
