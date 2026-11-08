from app.domain.scheduling import (
    InvalidScheduleError,
    scheduled_concert,
    validate_full_schedule,
)
from app.domain.entities import Artist, Concert, Festival, Stage
from app.ports import (
    ArtistRepository,
    ConcertRepository,
    FestivalRepository,
    NotificationPort,
    StageRepository,
)


class PublicationService:
    def __init__(
        self,
        festivals: FestivalRepository,
        concerts: ConcertRepository,
        artists: ArtistRepository,
        stages: StageRepository,
        notifications: NotificationPort,
    ) -> None:
        self.festivals = festivals
        self.concerts = concerts
        self.artists = artists
        self.stages = stages
        self.notifications = notifications

    def publish(self, festival_id: int) -> Festival | None:
        festival = self.festivals.get(festival_id)
        if festival is None:
            return None
        concerts = self.concerts.list_for_festival(festival_id)
        scheduled_concerts = []
        for concert in concerts:
            concert_festival = self.festivals.get(concert.festival_id)
            artist = self.artists.get(concert.artist_id)
            stage = self.stages.get(concert.stage_id)
            if concert_festival is None or artist is None or stage is None:
                raise InvalidScheduleError(
                    "Un concert référence un festival, un artiste ou une scène introuvable"
                )
            if (
                concert.id is None
                or concert_festival.id is None
                or artist.id is None
                or stage.id is None
            ):
                raise InvalidScheduleError("Les éléments du planning doivent avoir un identifiant")
            scheduled_concerts.append(
                scheduled_concert(
                    concert.id,
                    concert_festival.id,
                    artist.id,
                    stage.id,
                    stage.festival_id,
                    concert.start_time,
                    concert.end_time,
                    concert_festival.start_date,
                    concert_festival.end_date,
                    artist.required_equipment,
                    stage.available_equipment,
                )
            )
        validate_full_schedule(scheduled_concerts)
        festival.publish_schedule()
        published = self.festivals.save(festival)
        self.notifications.notify_schedule_change(
            festival_id, f"Le planning du festival {festival.name} a été publié."
        )
        return published
