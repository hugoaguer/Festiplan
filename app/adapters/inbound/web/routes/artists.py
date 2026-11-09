
from fastapi import APIRouter, Depends

from app.adapters.inbound.web.schemas.schemas import (
    ArtistCreate,
    ArtistRead,
)

from app.application.use_cases.create_artist import (
    CreateArtistUseCase,
)
from app.application.queries.list_artists import (
    ListArtistsQuery,
)

from app.bootstrap.container import (
    get_create_artist_use_case,
    get_list_artists_query,
)


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
    query: ListArtistsQuery = Depends(get_list_artists_query),
):
    return [
        out(artist)
        for artist in query.execute()
    ]


@router.post("", response_model=ArtistRead, status_code=201)
def create_artist(
    payload: ArtistCreate,
    use_case: CreateArtistUseCase = Depends(
        get_create_artist_use_case
    ),
):
    artist = use_case.execute(
        name=payload.name,
        genre=payload.genre,
        required_equipment=payload.required_equipment,
    )

    return out(artist)
