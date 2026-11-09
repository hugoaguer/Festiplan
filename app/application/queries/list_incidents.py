
from app.application.ports.outbound.incident_repository_port import (
    IncidentRepositoryPort,
)


class ListIncidentsQuery:

    def __init__(self, incident_repo: IncidentRepositoryPort):
        self.incident_repo = incident_repo

    def execute(self, concert_id: int | None = None):
        return self.incident_repo.list(concert_id)
