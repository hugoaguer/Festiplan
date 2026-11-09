
import logging

from app.application.ports.outbound.festival_repository_port import (
    FestivalRepositoryPort,
)
from app.application.ports.outbound.concert_repository_port import (
    ConcertRepositoryPort,
)
from app.application.ports.outbound.artist_repository_port import (
    ArtistRepositoryPort,
)
from app.application.ports.outbound.stage_repository_port import (
    StageRepositoryPort,
)
from app.application.ports.outbound.notification_sender import (
    NotificationSenderPort,
)

from app.domain.concert_rules import (
    validate_concert_dates,
    validate_stage_equipment,
    check_concert_overlap,
)


logger = logging.getLogger(__name__)


class PublishFestivalUseCase:

    def __init__(
        self,
        festival_repo: FestivalRepositoryPort,
        concert_repo: ConcertRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        stage_repo: StageRepositoryPort,
        notification_sender: NotificationSenderPort | None = None,
    ):
        self.festival_repo = festival_repo
        self.concert_repo = concert_repo
        self.artist_repo = artist_repo
        self.stage_repo = stage_repo
        self.notification_sender = notification_sender

    def execute(self, festival_id: int):
        festival = self.festival_repo.get(festival_id)

        if festival is None:
            return None

        if festival.status == "published":
            raise ValueError("Le planning est déjà publié")

        concerts = self.concert_repo.list_for_festival(festival_id)

        for concert in concerts:
            if concert.status == "cancelled":
                continue

            artist = self.artist_repo.get(concert.artist_id)
            stage = self.stage_repo.get(concert.stage_id)

            if artist is None or stage is None:
                raise ValueError("Artiste ou scène introuvable")

            if stage.festival_id != festival.id:
                raise ValueError(
                    "La scène n'appartient pas à ce festival"
                )

            validate_concert_dates(
                concert.start_time,
                concert.end_time,
            )

            if (
                concert.start_time < festival.start_date
                or concert.end_time > festival.end_date
            ):
                raise ValueError(
                    "Le concert doit se dérouler pendant le festival"
                )

            validate_stage_equipment(
                artist.required_equipment,
                stage.available_equipment,
            )

            for other in concerts:
                if other.id == concert.id:
                    continue

                if other.status == "cancelled":
                    continue

                if check_concert_overlap(
                    concert.start_time,
                    concert.end_time,
                    other.start_time,
                    other.end_time,
                ):
                    if other.stage_id == concert.stage_id:
                        raise ValueError(
                            "Conflit : la scène est déjà occupée"
                        )

                    if other.artist_id == concert.artist_id:
                        raise ValueError(
                            "Conflit : l'artiste est déjà programmé"
                        )

        festival.status = "published"
        saved_festival = self.festival_repo.save(festival)

        if self.notification_sender is not None:
            for concert in concerts:
                if concert.status == "cancelled":
                    continue

                try:
                    self.notification_sender.notify_schedule_change(
                        concert_id=concert.id,
                        message=(
                            f"Le planning du festival "
                            f"{festival.name} a été publié."
                        ),
                    )
                except Exception:
                    logger.exception(
                        "Erreur de notification pour le concert %s",
                        concert.id,
                    )

        return saved_festival
