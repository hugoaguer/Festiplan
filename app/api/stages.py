from fastapi import APIRouter, Depends, HTTPException

from app.application_ports import StageUseCases
from app.composition import get_stage_service
from app.domain.entities import Stage
from app.schemas import StageCreate, StageRead

router = APIRouter(prefix="/stages", tags=["stages"])


def _output(stage: Stage) -> dict:
    return {
        "id": stage.id,
        "festival_id": stage.festival_id,
        "name": stage.name,
        "capacity": stage.capacity,
        "available_equipment": [
            item for item in stage.available_equipment.split(",") if item
        ],
    }


@router.get("", response_model=list[StageRead])
def list_stages(
    festival_id: int,
    service: StageUseCases = Depends(get_stage_service),
):
    return [_output(stage) for stage in service.list_stages(festival_id)]


@router.post("", response_model=StageRead, status_code=201)
def create_stage(
    payload: StageCreate,
    service: StageUseCases = Depends(get_stage_service),
):
    try:
        stage = service.create_stage(
            payload.festival_id,
            payload.name,
            payload.capacity,
            payload.available_equipment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _output(stage)
