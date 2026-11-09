
from fastapi import APIRouter, Depends, HTTPException

from app.schemas import StageCreate, StageRead
from app.services.stage_service import StageService
from app.api.dependencies import get_stage_service


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
    service: StageService = Depends(get_stage_service),
):
    return [
        out(stage)
        for stage in service.list_stages(festival_id)
    ]


@router.post("", response_model=StageRead, status_code=201)
def create_stage(
    payload: StageCreate,
    service: StageService = Depends(get_stage_service),
):
    try:
        return out(service.create_stage(payload))
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
