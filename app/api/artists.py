
from fastapi import APIRouter, Depends

from app.schemas import ArtistCreate, ArtistRead
from app.services.artist_service import ArtistService
from app.api.dependencies import get_artist_service


router = APIRouter(prefix="/artists", tags=["artists"])


def out(artist):
    return {
        "id": artist.id,
        "name": artist.name,
        "genre": artist.genre,
        "required_equipment": [
            item.strip()
            for item in artist.required_equipment.split(",")
            if item.strip()
        ],
    }


@router.get("", response_model=list[ArtistRead])
def list_artists(
    service: ArtistService = Depends(get_artist_service),
):
    return [out(artist) for artist in service.list_artists()]


@router.post("", response_model=ArtistRead, status_code=201)
def create_artist(
    payload: ArtistCreate,
    service: ArtistService = Depends(get_artist_service),
):
    return out(service.create_artist(payload))
