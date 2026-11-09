
from app.application.ports.outbound.artist_repository_port import (
    ArtistRepositoryPort,
)


class CreateArtistUseCase:

    def __init__(self, artist_repo: ArtistRepositoryPort):
        self.artist_repo = artist_repo

    def execute(
        self,
        name: str,
        genre: str,
        required_equipment: list[str],
    ):
        artist = {
            "name": name,
            "genre": genre,
            "required_equipment": ",".join(required_equipment),
        }

        return self.artist_repo.create(artist)
