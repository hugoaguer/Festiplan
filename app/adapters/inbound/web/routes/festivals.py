
from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.web.schemas.schemas import (
    FestivalCreate,
    FestivalRead,
)

from app.application.use_cases.create_festival import (
    CreateFestivalUseCase,
)
from app.application.use_cases.publish_festival import (
    PublishFestivalUseCase,
)
from app.application.queries.list_festivals import (
    ListFestivalsQuery,
)

from app.bootstrap.container import (
    get_create_festival_use_case,
    get_publish_festival_use_case,
    get_list_festivals_query,
)


router = APIRouter(prefix="/festivals", tags=["festivals"])


@router.get("", response_model=list[FestivalRead])
def list_festivals(
    query: ListFestivalsQuery = Depends(get_list_festivals_query),
):
    return query.execute()


@router.post("", response_model=FestivalRead, status_code=201)
def create_festival(
    payload: FestivalCreate,
    use_case: CreateFestivalUseCase = Depends(
        get_create_festival_use_case
    ),
):
    try:
        return use_case.execute(
            name=payload.name,
            location=payload.location,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/{festival_id}/publish", response_model=FestivalRead)
def publish_festival(
    festival_id: int,
    use_case: PublishFestivalUseCase = Depends(
        get_publish_festival_use_case
    ),
):
    try:
        festival = use_case.execute(festival_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    if festival is None:
        raise HTTPException(
            status_code=404,
            detail="Festival introuvable",
        )

    return festival
