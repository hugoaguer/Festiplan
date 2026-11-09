
from datetime import datetime
from typing import Any, Protocol, TypedDict


class IncidentData(TypedDict):
    concert_id: int
    description: str
    occurred_at: datetime | None


class IncidentRepositoryPort(Protocol):

    def create(self, data: IncidentData) -> Any:
        ...

    def list(self, concert_id: int | None = None) -> list[Any]:
        ...
