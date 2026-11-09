
from app.application.ports.outbound.stage_repository_port import (
    StageRepositoryPort,
)
from app.application.ports.outbound.festival_repository_port import (
    FestivalRepositoryPort,
)


class CreateStageUseCase:

    def __init__(
        self,
        stage_repo: StageRepositoryPort,
        festival_repo: FestivalRepositoryPort,
    ):
        self.stage_repo = stage_repo
        self.festival_repo = festival_repo

    def execute(
        self,
        festival_id: int,
        name: str,
        capacity: int,
        available_equipment: list[str],
    ):
        festival = self.festival_repo.get(festival_id)

        if festival is None:
            raise ValueError("Festival introuvable")

        stage = {
            "festival_id": festival_id,
            "name": name,
            "capacity": capacity,
            "available_equipment": ",".join(
                available_equipment
            ),
        }

        return self.stage_repo.create(stage)
