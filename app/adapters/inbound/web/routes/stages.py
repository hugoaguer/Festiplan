
from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.web.schemas.schemas import (
    StageCreate,
    StageRead,
)

from app.application.use_cases.create_stage import (
    CreateStageUseCase,
)
from app.application.queries.list_stages import (
    ListStagesQuery,
)

from app.bootstrap.container import (
    get_create_stage_use_case,
    get_list_stages_query,
)


router = APIRouter(prefix="/stages", tags=["stages"])


def out(stage):
    return {
        "id": stage.id,
        "festival_id": stage.festival_id,
        "name": stage.name,
        "capacity": stage.capacity,
        "available_equipment": [
            item.strip()
            for item in stage.available_equipment.split(",")
            if item.strip()
        ],
    }


@router.get("", response_model=list[StageRead])
def list_stages(
    festival_id: int,
    query: ListStagesQuery = Depends(get_list_stages_query),
):
    return [
        out(stage)
        for stage in query.execute(festival_id)
    ]


@router.post("", response_model=StageRead, status_code=201)
def create_stage(
    payload: StageCreate,
    use_case: CreateStageUseCase = Depends(
        get_create_stage_use_case
    ),
):
    try:
        stage = use_case.execute(
            festival_id=payload.festival_id,
            name=payload.name,
            capacity=payload.capacity,
            available_equipment=payload.available_equipment,
        )

        return out(stage)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
