
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.sqlalchemy.models import Incident
from app.application.ports.outbound.incident_repository_port import (
    IncidentData,
    IncidentRepositoryPort,
)


class IncidentRepository(IncidentRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: IncidentData):
        incident = Incident(
            concert_id=data["concert_id"],
            description=data["description"],
        )
        if data["occurred_at"] is not None:
            incident.occurred_at = data["occurred_at"]

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        return incident

    def list(self, concert_id: int | None = None):
        query = self.db.query(Incident)

        if concert_id is not None:
            query = query.filter(Incident.concert_id == concert_id)

        return query.order_by(Incident.occurred_at.desc()).all()
