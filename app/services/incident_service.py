
from datetime import datetime

from app.application.ports.outbound.incident_repository_port import IncidentRepositoryPort
from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort


class IncidentService:

    def __init__(
        self,
        incident_repo: IncidentRepositoryPort,
        concert_repo: ConcertRepositoryPort,
    ):
        self.incident_repo = incident_repo
        self.concert_repo = concert_repo

    def create_incident(
        self,
        concert_id: int,
        description: str,
        occurred_at: datetime | None = None,
    ):
        concert = self.concert_repo.get(concert_id)

        if concert is None:
            raise ValueError("Concert introuvable")

        data = {
            "concert_id": concert_id,
            "description": description,
            "occurred_at": occurred_at,
        }

        return self.incident_repo.create(data)

    def list_incidents(self, concert_id: int | None = None):
        return self.incident_repo.list(concert_id)
