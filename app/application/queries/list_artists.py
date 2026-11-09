
from app.application.ports.outbound.artist_repository_port import (
    ArtistRepositoryPort,
)


class ListArtistsQuery:

    def __init__(self, artist_repo: ArtistRepositoryPort):
        self.artist_repo = artist_repo

    def execute(self):
        return self.artist_repo.list()
