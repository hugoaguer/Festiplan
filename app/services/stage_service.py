
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort


class StageService:

    def __init__(
        self,
        stage_repo: StageRepositoryPort,
        festival_repo: FestivalRepositoryPort,
    ):
        self.stage_repo = stage_repo
        self.festival_repo = festival_repo

    def list_stages(self, festival_id):
        return self.stage_repo.list_for_festival(festival_id)

    def create_stage(self, payload):
        festival = self.festival_repo.get(payload.festival_id)

        if festival is None:
            raise ValueError("Festival introuvable")

        stage = {
            "festival_id": payload.festival_id,
            "name": payload.name,
            "capacity": payload.capacity,
            "available_equipment": ",".join(
                payload.available_equipment
            ),
        }

        return self.stage_repo.create(stage)
