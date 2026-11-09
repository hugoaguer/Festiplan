
from datetime import datetime

from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort

from app.domain.concert_rules import (
    check_concert_overlap,
    validate_stage_equipment,
)


class RescheduleConcertUseCase:

    def __init__(
        self,
        concert_repo: ConcertRepositoryPort,
        festival_repo: FestivalRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        stage_repo: StageRepositoryPort,
    ):
        self.concert_repo = concert_repo
        self.festival_repo = festival_repo
        self.artist_repo = artist_repo
        self.stage_repo = stage_repo

    def execute(
        self,
        concert_id: int,
        start_time: datetime,
        end_time: datetime,
    ):
        concert = self.concert_repo.get(concert_id)

        if concert is None:
            return None

        festival = self.festival_repo.get(concert.festival_id)

        if festival is None:
            raise ValueError("Festival introuvable")

        if festival.status == "published":
            raise ValueError(
                "Impossible de modifier le planning : "
                "le planning est dÃ©jÃ  publiÃ©"
            )

        if concert.status == "cancelled":
            raise ValueError(
                "Impossible de dÃ©placer un concert annulÃ©"
            )

        artist = self.artist_repo.get(concert.artist_id)
        stage = self.stage_repo.get(concert.stage_id)

        if artist is None or stage is None:
            raise ValueError("Artiste ou scÃ¨ne introuvable")

        if stage.festival_id != festival.id:
            raise ValueError(
                "La scÃ¨ne n'appartient pas Ã  ce festival"
            )

        if start_time < festival.start_date or end_time > festival.end_date:
            raise ValueError(
                "Le concert doit se dÃ©rouler pendant le festival"
            )

        validate_stage_equipment(
            artist.required_equipment,
            stage.available_equipment,
        )

        for other in self.concert_repo.list_for_festival(festival.id):
            if other.id == concert.id:
                continue

            if check_concert_overlap(
                start_time,
                end_time,
                other.start_time,
                other.end_time,
            ):
                if other.stage_id == concert.stage_id:
                    raise ValueError(
                        "Conflit : la scÃ¨ne est dÃ©jÃ  occupÃ©e"
                    )

                if other.artist_id == concert.artist_id:
                    raise ValueError(
                        "Conflit : l'artiste est dÃ©jÃ  programmÃ©"
                    )

        concert.reschedule(start_time, end_time)

        return self.concert_repo.save(concert)
