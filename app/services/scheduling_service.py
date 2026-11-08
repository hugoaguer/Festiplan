import logging
from datetime import datetime

from app.domain.scheduling import (
    InvalidScheduleError,
    ScheduledConcert,
    ensure_no_conflicts,
    scheduled_concert,
    validate_concert_assignment,
)
from app.domain.entities import Artist, Concert, Festival, Stage
from app.ports import (
    ArtistRepository,
    ConcertRepository,
    FestivalRepository,
    NotificationDeliveryError,
    NotificationPort,
    StageRepository,
)

logger = logging.getLogger(__name__)


class SchedulingService:
    def __init__(
        self,
        concerts: ConcertRepository,
        festivals: FestivalRepository,
        artists: ArtistRepository,
        stages: StageRepository,
        notifications: NotificationPort,
    ) -> None:
        self.concerts = concerts
        self.festivals = festivals
        self.artists = artists
        self.stages = stages
        self.notifications = notifications

    def list_concerts(self, festival_id: int) -> list[Concert]:
        return list(self.concerts.list_for_festival(festival_id))

    def get_concert(self, concert_id: int) -> Concert | None:
        return self.concerts.get(concert_id)

    @staticmethod
    def _scheduled_concert(
        concert: Concert, festival: Festival, artist: Artist, stage: Stage
    ) -> ScheduledConcert:
        if concert.id is None or festival.id is None or artist.id is None or stage.id is None:
            raise InvalidScheduleError("Les éléments du planning doivent avoir un identifiant")
        return scheduled_concert(
            concert.id,
            festival.id,
            artist.id,
            stage.id,
            stage.festival_id,
            concert.start_time,
            concert.end_time,
            festival.start_date,
            festival.end_date,
            artist.required_equipment,
            stage.available_equipment,
        )

    def _check_conflicts(
        self, candidate: ScheduledConcert, exclude_id: int | None = None
    ) -> None:
        existing = []
        for concert in self.concerts.list_active():
            if concert.id == exclude_id:
                continue
            festival = self.festivals.get(concert.festival_id)
            artist = self.artists.get(concert.artist_id)
            stage = self.stages.get(concert.stage_id)
            if festival is None or artist is None or stage is None:
                raise InvalidScheduleError(
                    "Un concert existant référence un festival, un artiste ou une scène introuvable"
                )
            existing.append(self._scheduled_concert(concert, festival, artist, stage))
        ensure_no_conflicts(candidate, existing)

    def _validate_schedule(
        self,
        festival: Festival,
        artist: Artist,
        stage: Stage,
        start_time: datetime,
        end_time: datetime,
        exclude_id: int | None = None,
    ) -> None:
        if festival.id is None or artist.id is None or stage.id is None:
            raise InvalidScheduleError("Festival, artiste ou scène introuvable")
        candidate = scheduled_concert(
            exclude_id,
            festival.id,
            artist.id,
            stage.id,
            stage.festival_id,
            start_time,
            end_time,
            festival.start_date,
            festival.end_date,
            artist.required_equipment,
            stage.available_equipment,
        )
        validate_concert_assignment(candidate)
        self._check_conflicts(candidate, exclude_id=exclude_id)

    def create_concert(
        self,
        festival_id: int,
        artist_id: int,
        stage_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Concert:
        festival = self.festivals.get(festival_id)
        artist = self.artists.get(artist_id)
        stage = self.stages.get(stage_id)
        if festival is None or artist is None or stage is None:
            raise ValueError("Festival, artiste ou scène introuvable")
        festival.ensure_schedule_is_editable()
        self._validate_schedule(
            festival, artist, stage, start_time, end_time
        )
        return self.concerts.create(
            Concert(None, festival_id, artist_id, stage_id, start_time, end_time)
        )
    
    def reschedule_concert(
        self, concert_id: int, start_time: datetime, end_time: datetime
    ) -> tuple[Concert, bool] | None:
        concert = self.concerts.get(concert_id)
        if concert is None:
            return None
        festival = self.festivals.get(concert.festival_id)
        artist = self.artists.get(concert.artist_id)
        stage = self.stages.get(concert.stage_id)
        if festival is None or artist is None or stage is None:
            raise ValueError("Festival, artiste ou scène introuvable")
        festival.ensure_schedule_is_editable()
        self._validate_schedule(
            festival,
            artist,
            stage,
            start_time,
            end_time,
            exclude_id=concert.id,
        )
        concert.start_time = start_time
        concert.end_time = end_time
        concert = self.concerts.save(concert)
        if concert.id is None:
            raise InvalidScheduleError("Le concert enregistré doit avoir un identifiant")
        try:
            self.notifications.notify_schedule_change(
                concert.id, f"Concert déplacé au {concert.start_time.isoformat()}"
            )
        except NotificationDeliveryError:
            logger.exception(
                "Concert %s was rescheduled, but its notification could not be sent",
                concert.id,
            )
            return concert, False
        return concert, True
    
    def cancel_concert(self, concert_id: int) -> Concert | None:
        concert = self.concerts.get(concert_id)
        if concert is None: 
            return None
        festival = self.festivals.get(concert.festival_id)
        if festival is None:
            raise ValueError("Festival introuvable")
        festival.ensure_schedule_is_editable()
        concert.status = "cancelled"
        return self.concerts.save(concert)
    
    def get_schedule(self, festival_id: int) -> list[Concert]:
        return self.list_concerts(festival_id)
