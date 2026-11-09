
from sqlalchemy.orm import Session

from app.models import Concert as ConcertModel
from app.domain.concert import Concert as DomainConcert
from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.infrastructure.mappers.concert_mapper import (
    to_domain,
    to_model,
    update_model,
)


class ConcertRepository(ConcertRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def get(self, item_id: int):
        model = (
            self.db.query(ConcertModel)
            .filter(ConcertModel.id == item_id)
            .first()
        )

        return to_domain(model) if model is not None else None

    def list_for_festival(self, festival_id: int):
        models = (
            self.db.query(ConcertModel)
            .filter(
                ConcertModel.festival_id == festival_id,
                ConcertModel.status != "cancelled"
            )
            .order_by(ConcertModel.start_time)
            .all()
        )

        return [to_domain(model) for model in models]

    def create(self, item: DomainConcert):
        model = to_model(item)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return to_domain(model)

    def save(self, item: DomainConcert):
        model = (
            self.db.query(ConcertModel)
            .filter(ConcertModel.id == item.id)
            .first()
        )

        if model is None:
            raise ValueError("Concert introuvable")

        update_model(model, item)

        self.db.commit()
        self.db.refresh(model)

        return to_domain(model)
