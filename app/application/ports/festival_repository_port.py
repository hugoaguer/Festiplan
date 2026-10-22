
from typing import Protocol, Any


class FestivalRepositoryPort(Protocol):

    def list(self) -> list[Any]:
        ...

    def get(self, item_id: int) -> Any | None:
        ...

    def create(self, item: Any) -> Any:
        ...
