from fastapi import APIRouter, Depends, HTTPException

from app.application_ports import IncidentUseCases
from app.composition import get_incident_service
from app.schemas import IncidentCreate, IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(
    payload: IncidentCreate,
    service: IncidentUseCases = Depends(get_incident_service),
):
    try:
        incident = service.create_incident(
            payload.concert_id, payload.description, payload.occurred_at
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if incident is None:
        raise HTTPException(status_code=404, detail="Concert introuvable")
    return incident


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    concert_id: int | None = None,
    service: IncidentUseCases = Depends(get_incident_service),
):
    return service.list_incidents(concert_id)
