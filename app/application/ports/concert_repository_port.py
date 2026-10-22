from typing import Protocol, Any


class ConcertRepositoryPort(Protocol):

    def get(self, item_id: int) -> Any | None:
        ...

    def list_for_festival(self, festival_id: int) -> list[Any]:
        ...

    def create(self, item: Any) -> Any:
        ...