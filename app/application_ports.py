from datetime import datetime
from typing import Protocol

from app.domain.entities import Artist, Concert, Festival, Incident, Stage


class FestivalUseCases(Protocol):
    def list_festivals(self) -> list[Festival]: ...

    def create_festival(
        self, name: str, location: str, start_date: datetime, end_date: datetime
    ) -> Festival: ...


class ArtistUseCases(Protocol):
    def list_artists(self) -> list[Artist]: ...

    def create_artist(
        self, name: str, genre: str, required_equipment: list[str]
    ) -> Artist: ...


class StageUseCases(Protocol):
    def list_stages(self, festival_id: int) -> list[Stage]: ...

    def create_stage(
        self,
        festival_id: int,
        name: str,
        capacity: int,
        available_equipment: list[str],
    ) -> Stage: ...


class SchedulingUseCases(Protocol):
    def list_concerts(self, festival_id: int) -> list[Concert]: ...

    def get_concert(self, concert_id: int) -> Concert | None: ...

    def create_concert(
        self,
        festival_id: int,
        artist_id: int,
        stage_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Concert: ...

    def reschedule_concert(
        self, concert_id: int, start_time: datetime, end_time: datetime
    ) -> tuple[Concert, bool] | None: ...

    def cancel_concert(self, concert_id: int) -> Concert | None: ...

    def get_schedule(self, festival_id: int) -> list[Concert]: ...


class PublicationUseCases(Protocol):
    def publish(self, festival_id: int) -> Festival | None: ...


class IncidentUseCases(Protocol):
    def create_incident(
        self, concert_id: int, description: str, occurred_at: datetime | None
    ) -> Incident | None: ...

    def list_incidents(self, concert_id: int | None = None) -> list[Incident]: ...
