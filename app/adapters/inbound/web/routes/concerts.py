
from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.web.schemas.schemas import (
    ConcertCreate,
    ConcertRead,
    ConcertReschedule,
)

from app.application.queries.get_concert import GetConcertQuery
from app.application.queries.list_concerts import ListConcertsQuery

from app.application.use_cases.create_concert import CreateConcertUseCase
from app.application.use_cases.reschedule_concert import RescheduleConcertUseCase
from app.application.use_cases.cancel_concert import CancelConcertUseCase

from app.bootstrap.container import (
    get_concert_query,
    get_list_concerts_query,
    get_create_concert_use_case,
    get_reschedule_concert_use_case,
    get_cancel_concert_use_case,
)


router = APIRouter(prefix="/concerts", tags=["concerts"])


# ==========================================
# CONSULTATION
# ==========================================

@router.get("", response_model=list[ConcertRead])
def list_concerts(
    festival_id: int,
    query: ListConcertsQuery = Depends(get_list_concerts_query),
):
    return query.execute(festival_id)


@router.get("/schedule/{festival_id}", response_model=list[ConcertRead])
def get_schedule(
    festival_id: int,
    query: ListConcertsQuery = Depends(get_list_concerts_query),
):
    return query.execute(festival_id)


@router.get("/{concert_id}", response_model=ConcertRead)
def get_concert(
    concert_id: int,
    query: GetConcertQuery = Depends(get_concert_query),
):
    concert = query.execute(concert_id)

    if concert is None:
        raise HTTPException(
            status_code=404,
            detail="Concert introuvable",
        )

    return concert


# ==========================================
# CREATION
# ==========================================

@router.post("", response_model=ConcertRead, status_code=201)
def create_concert(
    payload: ConcertCreate,
    use_case: CreateConcertUseCase = Depends(
        get_create_concert_use_case
    ),
):
    try:
        return use_case.execute(
            festival_id=payload.festival_id,
            artist_id=payload.artist_id,
            stage_id=payload.stage_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ==========================================
# MODIFICATION
# ==========================================

@router.patch("/{concert_id}/reschedule", response_model=ConcertRead)
def reschedule_concert(
    concert_id: int,
    payload: ConcertReschedule,
    use_case: RescheduleConcertUseCase = Depends(
        get_reschedule_concert_use_case
    ),
):
    try:
        concert = use_case.execute(
            concert_id=concert_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if concert is None:
        raise HTTPException(
            status_code=404,
            detail="Concert introuvable",
        )

    return concert


# ==========================================
# ANNULATION
# ==========================================

@router.post("/{concert_id}/cancel", response_model=ConcertRead)
def cancel_concert(
    concert_id: int,
    use_case: CancelConcertUseCase = Depends(
        get_cancel_concert_use_case
    ),
):
    try:
        concert = use_case.execute(concert_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if concert is None:
        raise HTTPException(
            status_code=404,
            detail="Concert introuvable",
        )

    return concert
