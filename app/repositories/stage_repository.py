
from sqlalchemy.orm import Session

from app.models import Stage
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort


class StageRepository(StageRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def list_for_festival(self, festival_id: int):
        return (
            self.db.query(Stage)
            .filter(Stage.festival_id == festival_id)
            .all()
        )

    def get(self, item_id: int):
        return (
            self.db.query(Stage)
            .filter(Stage.id == item_id)
            .first()
        )

    def create(self, data):
        stage = Stage(
            festival_id=data["festival_id"],
            name=data["name"],
            capacity=data["capacity"],
            available_equipment=data["available_equipment"],
        )

        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)

        return stage
