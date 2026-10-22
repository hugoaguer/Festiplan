
from sqlalchemy.orm import Session

from app.models import Festival
from app.application.ports.festival_repository_port import FestivalRepositoryPort
from app.repositories.festival_repository import FestivalRepository


class FestivalService:

    def __init__(
        self,
        db: Session,
        repo: FestivalRepositoryPort | None = None
    ):
        self.repo = repo if repo is not None else FestivalRepository(db)

    def list_festivals(self):
        return self.repo.list()

    def create_festival(self, payload):
        if payload.end_date <= payload.start_date:
            raise ValueError(
                "La date de fin doit être postérieure à la date de début"
            )

        festival = Festival(
            name=payload.name,
            location=payload.location,
            start_date=payload.start_date,
            end_date=payload.end_date
        )

        return self.repo.create(festival)

    def publish(self, festival_id):
        festival = self.repo.get(festival_id)

        if festival is None:
            return None

        festival.status = "published"

        return self.repo.save(festival)
