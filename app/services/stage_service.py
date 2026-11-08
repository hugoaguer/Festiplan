from app.domain.scheduling import validate_capacity
from app.domain.entities import Stage
from app.ports import FestivalRepository, StageRepository


class StageService:
    def __init__(
        self, stages: StageRepository, festivals: FestivalRepository
    ) -> None:
        self.stages = stages
        self.festivals = festivals

    def list_stages(self, festival_id: int) -> list[Stage]:
        return list(self.stages.list_for_festival(festival_id))

    def create_stage(
        self,
        festival_id: int,
        name: str,
        capacity: int,
        available_equipment: list[str],
    ) -> Stage:
        validate_capacity(capacity)
        if self.festivals.get(festival_id) is None:
            raise ValueError("Festival introuvable")
        return self.stages.create(
            Stage(
                None,
                festival_id,
                name,
                capacity,
                ",".join(available_equipment),
            )
        )
