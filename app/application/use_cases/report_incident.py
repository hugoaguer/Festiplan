
from datetime import datetime

from app.application.ports.outbound.incident_repository_port import (
    IncidentRepositoryPort,
)
from app.application.ports.outbound.concert_repository_port import (
    ConcertRepositoryPort,
)


class ReportIncidentUseCase:
    def __init__(
        self,
        incident_repo: IncidentRepositoryPort,
        concert_repo: ConcertRepositoryPort,
    ):
        self.incident_repo = incident_repo
        self.concert_repo = concert_repo

    def execute(
        self,
        concert_id: int,
        description: str,
        occurred_at: datetime | None = None,
    ):
        concert = self.concert_repo.get(concert_id)

        if concert is None:
            raise ValueError("Concert introuvable")

        if not description or not description.strip():
            raise ValueError(
                "La description de l'incident est obligatoire"
            )

        return self.incident_repo.create(
            {
                "concert_id": concert_id,
                "description": description,
                "occurred_at": occurred_at,
            }
        )
