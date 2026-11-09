
from app.domain.concert import Concert as DomainConcert
from app.adapters.outbound.persistence.sqlalchemy.models import Concert as ConcertModel


def to_domain(model: ConcertModel) -> DomainConcert:
    return DomainConcert(
        id=model.id,
        festival_id=model.festival_id,
        artist_id=model.artist_id,
        stage_id=model.stage_id,
        start_time=model.start_time,
        end_time=model.end_time,
        status=model.status
    )


def to_model(concert: DomainConcert) -> ConcertModel:
    model = ConcertModel(
        festival_id=concert.festival_id,
        artist_id=concert.artist_id,
        stage_id=concert.stage_id,
        start_time=concert.start_time,
        end_time=concert.end_time,
        status=concert.status
    )

    if concert.id is not None:
        model.id = concert.id

    return model


def update_model(
    model: ConcertModel,
    concert: DomainConcert
) -> ConcertModel:
    model.start_time = concert.start_time
    model.end_time = concert.end_time
    model.status = concert.status

    return model
