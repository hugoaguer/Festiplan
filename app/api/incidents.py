
from fastapi import APIRouter, Depends, HTTPException

from app.schemas import IncidentCreate, IncidentRead
from app.services.incident_service import IncidentService
from app.api.dependencies import get_incident_service


router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(
    payload: IncidentCreate,
    service: IncidentService = Depends(get_incident_service),
):
    try:
        return service.create_incident(
            concert_id=payload.concert_id,
            description=payload.description,
            occurred_at=payload.occurred_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    concert_id: int | None = None,
    service: IncidentService = Depends(get_incident_service),
):
    return service.list_incidents(concert_id)
