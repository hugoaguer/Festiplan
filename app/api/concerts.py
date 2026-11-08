from fastapi import APIRouter, Depends, HTTPException, Response

from app.application_ports import SchedulingUseCases
from app.composition import get_scheduling_service
from app.schemas import ConcertCreate, ConcertRead, ConcertReschedule

router = APIRouter(prefix="/concerts", tags=["concerts"])


@router.get("", response_model=list[ConcertRead])
def list_concerts(
    festival_id: int,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    return service.list_concerts(festival_id)


@router.get("/{concert_id}", response_model=ConcertRead)
def get_concert(
    concert_id: int,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    concert = service.get_concert(concert_id)
    if concert is None:
        raise HTTPException(status_code=404, detail="Concert introuvable")
    return concert


@router.post("", response_model=ConcertRead, status_code=201)
def create_concert(
    payload: ConcertCreate,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    try:
        return service.create_concert(
            payload.festival_id,
            payload.artist_id,
            payload.stage_id,
            payload.start_time,
            payload.end_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{concert_id}/reschedule", response_model=ConcertRead)
def reschedule_concert(
    concert_id: int,
    payload: ConcertReschedule,
    response: Response,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    try:
        result = service.reschedule_concert(
            concert_id, payload.start_time, payload.end_time
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Concert introuvable")
    concert, notification_sent = result
    response.headers["X-Notification-Status"] = (
        "sent" if notification_sent else "failed"
    )
    return concert


@router.post("/{concert_id}/cancel", response_model=ConcertRead)
def cancel_concert(
    concert_id: int,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    try:
        concert = service.cancel_concert(concert_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if concert is None:
        raise HTTPException(status_code=404, detail="Concert introuvable")
    return concert


@router.get("/schedule/{festival_id}", response_model=list[ConcertRead])
def get_schedule(
    festival_id: int,
    service: SchedulingUseCases = Depends(get_scheduling_service),
):
    return service.get_schedule(festival_id)
