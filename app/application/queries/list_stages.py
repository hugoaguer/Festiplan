
from app.application.ports.outbound.stage_repository_port import (
    StageRepositoryPort,
)


class ListStagesQuery:

    def __init__(self, stage_repo: StageRepositoryPort):
        self.stage_repo = stage_repo

    def execute(self, festival_id: int):
        return self.stage_repo.list_for_festival(festival_id)
