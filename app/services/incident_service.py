from datetime import datetime

from app.domain.entities import Incident
from app.domain.scheduling import validate_incident_description
from app.ports import ConcertRepository, IncidentRepository


class IncidentService:
    def __init__(
        self, concerts: ConcertRepository, incidents: IncidentRepository
    ) -> None:
        self.concerts = concerts
        self.incidents = incidents

    def create_incident(
        self, concert_id: int, description: str, occurred_at: datetime | None
    ) -> Incident | None:
        normalized_description = validate_incident_description(description)
        if self.concerts.get(concert_id) is None:
            return None
        return self.incidents.create(
            Incident(None, concert_id, normalized_description, occurred_at)
        )

    def list_incidents(self, concert_id: int | None = None) -> list[Incident]:
        return list(self.incidents.list_for_concert(concert_id))
