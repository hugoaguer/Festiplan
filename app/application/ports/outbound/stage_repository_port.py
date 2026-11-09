from typing import Any, Protocol


class StageRepositoryPort(Protocol):

    def list_for_festival(self, festival_id: int) -> list[Any]:
        ...

    def get(self, item_id: int) -> Any | None:
        ...

    def create(self, item: Any) -> Any:
        ...