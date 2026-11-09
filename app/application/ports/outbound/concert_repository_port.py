
from typing import Protocol

from app.domain.concert import Concert


class ConcertRepositoryPort(Protocol):

    def get(self, item_id: int) -> Concert | None:
        ...

    def list_for_festival(self, festival_id: int) -> list[Concert]:
        ...

    def create(self, item: Concert) -> Concert:
        ...

    def save(self, item: Concert) -> Concert:
        ...
