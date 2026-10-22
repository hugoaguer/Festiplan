
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ConcertCreate, ConcertRead, ConcertReschedule
from app.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/concerts", tags=["concerts"])


@router.get("", response_model=list[ConcertRead])
def list_concerts(festival_id: int, db: Session = Depends(get_db)):
    service = SchedulingService(db)
    return service.list_concerts(festival_id)


@router.get("/{concert_id}", response_model=ConcertRead)
def get_concert(concert_id: int, db: Session = Depends(get_db)):
    service = SchedulingService(db)
    concert = service.get_concert(concert_id)

    if concert is None:
        raise HTTPException(
            status_code=404,
            detail="Concert introuvable"
        )

    return concert


@router.post("", response_model=ConcertRead, status_code=201)
def create_concert(
    payload: ConcertCreate,
    db: Session = Depends(get_db)
):
    service = SchedulingService(db)

    try:
        return service.create_concert(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{concert_id}/reschedule", response_model=ConcertRead)
def reschedule_concert(
    concert_id: int,
    payload: ConcertReschedule,
    db: Session = Depends(get_db)
):
    service = SchedulingService(db)

    try:
        concert = service.reschedule_concert(concert_id, payload)

        if concert is None:
            raise HTTPException(
                status_code=404,
                detail="Concert introuvable"
            )

        return concert

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{concert_id}/cancel", response_model=ConcertRead)
def cancel_concert(concert_id: int, db: Session = Depends(get_db)):
    service = SchedulingService(db)
    concert = service.cancel_concert(concert_id)

    if concert is None:
        raise HTTPException(
            status_code=404,
            detail="Concert introuvable"
        )

    return concert


@router.get("/schedule/{festival_id}", response_model=list[ConcertRead])
def get_schedule(festival_id: int, db: Session = Depends(get_db)):
    service = SchedulingService(db)
    return service.get_schedule(festival_id)
