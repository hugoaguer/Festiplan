from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.domain.entities import Artist, Concert, Festival, Incident, Stage
from app.models import (
    Artist as ArtistModel,
    Concert as ConcertModel,
    Festival as FestivalModel,
    Incident as IncidentModel,
    Stage as StageModel,
)


class SQLAlchemyFestivalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> Sequence[Festival]:
        rows = self.session.query(FestivalModel).order_by(FestivalModel.id).all()
        return [_festival_entity(row) for row in rows]

    def get(self, festival_id: int) -> Festival | None:
        row = self.session.get(FestivalModel, festival_id)
        return _festival_entity(row) if row is not None else None

    def create(self, festival: Festival) -> Festival:
        row = FestivalModel(
            name=festival.name,
            location=festival.location,
            start_date=festival.start_date,
            end_date=festival.end_date,
            status=festival.status,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _festival_entity(row)

    def save(self, festival: Festival) -> Festival:
        if festival.id is None:
            raise ValueError("Impossible d'enregistrer un festival sans identifiant")
        row = self.session.get(FestivalModel, festival.id)
        if row is None:
            raise ValueError("Festival introuvable")
        row.name = festival.name
        row.location = festival.location
        row.start_date = festival.start_date
        row.end_date = festival.end_date
        row.status = festival.status
        self.session.commit()
        self.session.refresh(row)
        return _festival_entity(row)


class SQLAlchemyArtistRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> Sequence[Artist]:
        rows = self.session.query(ArtistModel).order_by(ArtistModel.name).all()
        return [_artist_entity(row) for row in rows]

    def get(self, artist_id: int) -> Artist | None:
        row = self.session.get(ArtistModel, artist_id)
        return _artist_entity(row) if row is not None else None

    def create(self, artist: Artist) -> Artist:
        row = ArtistModel(
            name=artist.name,
            genre=artist.genre,
            required_equipment=artist.required_equipment,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _artist_entity(row)


class SQLAlchemyStageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_festival(self, festival_id: int) -> Sequence[Stage]:
        rows = (
            self.session.query(StageModel)
            .filter(StageModel.festival_id == festival_id)
            .order_by(StageModel.id)
            .all()
        )
        return [_stage_entity(row) for row in rows]

    def get(self, stage_id: int) -> Stage | None:
        row = self.session.get(StageModel, stage_id)
        return _stage_entity(row) if row is not None else None

    def create(self, stage: Stage) -> Stage:
        row = StageModel(
            festival_id=stage.festival_id,
            name=stage.name,
            capacity=stage.capacity,
            available_equipment=stage.available_equipment,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _stage_entity(row)


class SQLAlchemyConcertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, concert_id: int) -> Concert | None:
        row = self.session.get(ConcertModel, concert_id)
        return _concert_entity(row) if row is not None else None

    def list_for_festival(self, festival_id: int) -> Sequence[Concert]:
        rows = (
            self.session.query(ConcertModel)
            .filter(
                ConcertModel.festival_id == festival_id,
                ConcertModel.status != "cancelled",
            )
            .order_by(ConcertModel.start_time)
            .all()
        )
        return [_concert_entity(row) for row in rows]

    def list_active(self) -> Sequence[Concert]:
        rows = (
            self.session.query(ConcertModel)
            .filter(ConcertModel.status != "cancelled")
            .all()
        )
        return [_concert_entity(row) for row in rows]

    def create(self, concert: Concert) -> Concert:
        row = ConcertModel(
            festival_id=concert.festival_id,
            artist_id=concert.artist_id,
            stage_id=concert.stage_id,
            start_time=concert.start_time,
            end_time=concert.end_time,
            status=concert.status,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _concert_entity(row)

    def save(self, concert: Concert) -> Concert:
        if concert.id is None:
            raise ValueError("Impossible d'enregistrer un concert sans identifiant")
        row = self.session.get(ConcertModel, concert.id)
        if row is None:
            raise ValueError("Concert introuvable")
        row.start_time = concert.start_time
        row.end_time = concert.end_time
        row.status = concert.status
        self.session.commit()
        self.session.refresh(row)
        return _concert_entity(row)


class SQLAlchemyIncidentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_concert(self, concert_id: int | None) -> Sequence[Incident]:
        query = self.session.query(IncidentModel)
        if concert_id is not None:
            query = query.filter(IncidentModel.concert_id == concert_id)
        rows = query.order_by(IncidentModel.occurred_at.desc()).all()
        return [_incident_entity(row) for row in rows]

    def create(self, incident: Incident) -> Incident:
        row = IncidentModel(
            concert_id=incident.concert_id,
            description=incident.description,
            resolved=incident.resolved,
        )
        if incident.occurred_at is not None:
            row.occurred_at = incident.occurred_at
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return _incident_entity(row)


def _festival_entity(row: FestivalModel) -> Festival:
    return Festival(row.id, row.name, row.location, row.start_date, row.end_date, row.status)


def _artist_entity(row: ArtistModel) -> Artist:
    return Artist(row.id, row.name, row.genre, row.required_equipment)


def _stage_entity(row: StageModel) -> Stage:
    return Stage(row.id, row.festival_id, row.name, row.capacity, row.available_equipment)


def _concert_entity(row: ConcertModel) -> Concert:
    return Concert(
        row.id,
        row.festival_id,
        row.artist_id,
        row.stage_id,
        row.start_time,
        row.end_time,
        row.status,
    )


def _incident_entity(row: IncidentModel) -> Incident:
    return Incident(row.id, row.concert_id, row.description, row.occurred_at, row.resolved)
