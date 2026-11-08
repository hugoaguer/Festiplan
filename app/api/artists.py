from fastapi import APIRouter, Depends

from app.application_ports import ArtistUseCases
from app.composition import get_artist_service
from app.domain.entities import Artist
from app.schemas import ArtistCreate, ArtistRead

router = APIRouter(prefix="/artists", tags=["artists"])


def _output(artist: Artist) -> dict:
    return {
        "id": artist.id,
        "name": artist.name,
        "genre": artist.genre,
        "required_equipment": [
            item for item in artist.required_equipment.split(",") if item
        ],
    }


@router.get("", response_model=list[ArtistRead])
def list_artists(
    service: ArtistUseCases = Depends(get_artist_service),
):
    return [_output(artist) for artist in service.list_artists()]


@router.post("", response_model=ArtistRead, status_code=201)
def create_artist(
    payload: ArtistCreate,
    service: ArtistUseCases = Depends(get_artist_service),
):
    artist = service.create_artist(
        payload.name, payload.genre, payload.required_equipment
    )
    return _output(artist)
