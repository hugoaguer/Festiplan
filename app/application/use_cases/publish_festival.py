
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort
from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort

from app.domain.concert_rules import (
    validate_concert_dates,
    validate_stage_equipment,
    check_concert_overlap,
)


class PublishFestivalUseCase:

    def __init__(
        self,
        festival_repo: FestivalRepositoryPort,
        concert_repo: ConcertRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        stage_repo: StageRepositoryPort,
    ):
        self.festival_repo = festival_repo
        self.concert_repo = concert_repo
        self.artist_repo = artist_repo
        self.stage_repo = stage_repo

    def execute(self, festival_id: int):
        festival = self.festival_repo.get(festival_id)

        if festival is None:
            return None

        if festival.status == "published":
            raise ValueError("Le planning est dÃ©jÃ  publiÃ©")

        concerts = self.concert_repo.list_for_festival(festival_id)

        for concert in concerts:
            if concert.status == "cancelled":
                continue

            artist = self.artist_repo.get(concert.artist_id)
            stage = self.stage_repo.get(concert.stage_id)

            if artist is None or stage is None:
                raise ValueError("Artiste ou scÃ¨ne introuvable")

            if stage.festival_id != festival.id:
                raise ValueError(
                    "La scÃ¨ne n'appartient pas Ã  ce festival"
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
                    "Le concert doit se dÃ©rouler pendant le festival"
                )

            validate_stage_equipment(
                artist.required_equipment,
                stage.available_equipment,
            )

            for other in concerts:
                if other.id == concert.id:
                    continue

                if check_concert_overlap(
                    concert.start_time,
                    concert.end_time,
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

        festival.status = "published"

        return self.festival_repo.save(festival)
