
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort


class FestivalService:

    def __init__(
        self,
        db=None,
        repo: FestivalRepositoryPort | None = None,
    ):
        if repo is None:
            if db is None:
                raise ValueError(
                    "Une session ou un repository est nÃ©cessaire"
                )

            from app.repositories.festival_repository import FestivalRepository

            repo = FestivalRepository(db)

        self.repo = repo

    def list_festivals(self):
        return self.repo.list()

    def create_festival(self, payload):
        if payload.end_date <= payload.start_date:
            raise ValueError(
                "La date de fin doit Ãªtre postÃ©rieure Ã  la date de dÃ©but"
            )

        data = {
            "name": payload.name,
            "location": payload.location,
            "start_date": payload.start_date,
            "end_date": payload.end_date,
        }

        return self.repo.create(data)
