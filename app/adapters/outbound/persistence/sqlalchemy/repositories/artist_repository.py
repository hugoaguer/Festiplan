
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.sqlalchemy.models import Artist
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort


class ArtistRepository(ArtistRepositoryPort):

    def __init__(self, db: Session):
        self.db = db

    def list(self):
        return self.db.query(Artist).all()

    def get(self, item_id: int):
        return (
            self.db.query(Artist)
            .filter(Artist.id == item_id)
            .first()
        )

    def create(self, data):
        artist = Artist(
            name=data["name"],
            genre=data["genre"],
            required_equipment=data["required_equipment"],
        )

        self.db.add(artist)
        self.db.commit()
        self.db.refresh(artist)

        return artist
