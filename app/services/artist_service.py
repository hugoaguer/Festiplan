
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort


class ArtistService:

    def __init__(self, repo: ArtistRepositoryPort):
        self.repo = repo

    def list_artists(self):
        return self.repo.list()

    def create_artist(self, payload):
        artist = {
            "name": payload.name,
            "genre": payload.genre,
            "required_equipment": ",".join(
                payload.required_equipment
            ),
        }

        return self.repo.create(artist)
