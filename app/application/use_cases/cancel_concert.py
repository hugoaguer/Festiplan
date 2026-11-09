
from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort


class CancelConcertUseCase:

    def __init__(
        self,
        concert_repo: ConcertRepositoryPort,
        festival_repo: FestivalRepositoryPort,
    ):
        self.concert_repo = concert_repo
        self.festival_repo = festival_repo

    def execute(self, concert_id: int):
        concert = self.concert_repo.get(concert_id)

        if concert is None:
            return None

        festival = self.festival_repo.get(concert.festival_id)

        if festival is None:
            raise ValueError("Festival introuvable")

        if festival.status == "published":
            raise ValueError(
                "Impossible de modifier le planning : "
                "le planning est dÃ©jÃ  publiÃ©"
            )

        concert.cancel()

        return self.concert_repo.save(concert)
