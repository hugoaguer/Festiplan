
from sqlalchemy.orm import Session

from app.models import Festival
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort


class FestivalRepository(FestivalRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def list(self):
        return (
            self.db.query(Festival)
            .order_by(Festival.id)
            .all()
        )

    def get(self, item_id: int):
        return (
            self.db.query(Festival)
            .filter(Festival.id == item_id)
            .first()
        )

    def create(self, data):
        festival = Festival(
            name=data["name"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )

        self.db.add(festival)
        self.db.commit()
        self.db.refresh(festival)

        return festival

    def save(self, item):
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item
