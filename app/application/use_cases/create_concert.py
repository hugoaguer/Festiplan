
from datetime import datetime

from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort

from app.domain.concert import Concert
from app.domain.concert_rules import (
    check_concert_overlap,
    validate_concert_dates,
    validate_stage_equipment,
)


class CreateConcertUseCase:

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
        festival_id: int,
        artist_id: int,
        stage_id: int,
        start_time: datetime,
        end_time: datetime,
    ):
        festival = self.festival_repo.get(festival_id)

        if festival is None:
            raise ValueError("Festival introuvable")

        if festival.status == "published":
            raise ValueError(
                "Impossible de modifier le planning : "
                "le planning est dÃ©jÃ  publiÃ©"
            )

        artist = self.artist_repo.get(artist_id)
        stage = self.stage_repo.get(stage_id)

        if artist is None or stage is None:
            raise ValueError("Artiste ou scÃ¨ne introuvable")

        if stage.festival_id != festival.id:
            raise ValueError(
                "La scÃ¨ne n'appartient pas Ã  ce festival"
            )

        validate_concert_dates(start_time, end_time)

        if (
            start_time < festival.start_date
            or end_time > festival.end_date
        ):
            raise ValueError(
                "Le concert doit se dÃ©rouler pendant le festival"
            )

        validate_stage_equipment(
            artist.required_equipment,
            stage.available_equipment
        )

        concerts = self.concert_repo.list_for_festival(festival_id)

        for other in concerts:
            if check_concert_overlap(
                start_time,
                end_time,
                other.start_time,
                other.end_time,
            ):
                if other.stage_id == stage_id:
                    raise ValueError(
                        "Conflit : la scÃ¨ne est dÃ©jÃ  occupÃ©e"
                    )

                if other.artist_id == artist_id:
                    raise ValueError(
                        "Conflit : l'artiste est dÃ©jÃ  programmÃ©"
                    )

        concert = Concert(
            id=None,
            festival_id=festival_id,
            artist_id=artist_id,
            stage_id=stage_id,
            start_time=start_time,
            end_time=end_time,
        )

        return self.concert_repo.create(concert)
