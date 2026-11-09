
from fastapi import APIRouter, Depends, HTTPException

from app.adapters.inbound.web.schemas.schemas import (
    IncidentCreate,
    IncidentRead,
)

from app.application.use_cases.report_incident import (
    ReportIncidentUseCase,
)
from app.application.queries.list_incidents import (
    ListIncidentsQuery,
)

from app.bootstrap.container import (
    get_report_incident_use_case,
    get_list_incidents_query,
)


router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(
    payload: IncidentCreate,
    use_case: ReportIncidentUseCase = Depends(
        get_report_incident_use_case
    ),
):
    try:
        return use_case.execute(
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
    query: ListIncidentsQuery = Depends(
        get_list_incidents_query
    ),
):
    return query.execute(concert_id)
