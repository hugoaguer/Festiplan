from app.domain.entities import Artist
from app.ports import ArtistRepository


class ArtistService:
    def __init__(self, artists: ArtistRepository) -> None:
        self.artists = artists

    def list_artists(self) -> list[Artist]:
        return list(self.artists.list())

    def create_artist(
        self, name: str, genre: str, required_equipment: list[str]
    ) -> Artist:
        return self.artists.create(
            Artist(None, name, genre, ",".join(required_equipment))
        )
