from fastapi import APIRouter, Depends, HTTPException

from app.application_ports import FestivalUseCases, PublicationUseCases
from app.composition import get_festival_service, get_publication_service
from app.schemas import FestivalCreate, FestivalRead

router = APIRouter(prefix="/festivals", tags=["festivals"])


@router.get("", response_model=list[FestivalRead])
def list_festivals(
    service: FestivalUseCases = Depends(get_festival_service),
):
    return service.list_festivals()


@router.post("", response_model=FestivalRead, status_code=201)
def create_festival(
    payload: FestivalCreate,
    service: FestivalUseCases = Depends(get_festival_service),
):
    try:
        return service.create_festival(
            payload.name, payload.location, payload.start_date, payload.end_date
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{festival_id}/publish", response_model=FestivalRead)
def publish_festival(
    festival_id: int,
    service: PublicationUseCases = Depends(get_publication_service),
):
    try:
        festival = service.publish(festival_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if festival is None:
        raise HTTPException(status_code=404, detail="Festival introuvable")
    return festival
