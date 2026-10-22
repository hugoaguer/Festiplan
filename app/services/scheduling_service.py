
import logging

from sqlalchemy.orm import Session

from app.models import Artist, Concert, Festival, Stage
from app.repositories.concert_repository import ConcertRepository
from app.services.notification_service import NotificationService
from app.utils.date_helpers import overlaps


logger = logging.getLogger(__name__)


class SchedulingService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = ConcertRepository(db)
        self.notifications = NotificationService()

    # Récupérer tous les concerts d'un festival
    def list_concerts(self, festival_id):
        return self.repo.list_for_festival(festival_id)

    # Récupérer un concert par son identifiant
    def get_concert(self, concert_id):
        return self.repo.get(concert_id)

    # Vérifier si le planning est modifiable
    def _check_planning_status(self, festival_id):
        festival = (
            self.db.query(Festival)
            .filter(Festival.id == festival_id)
            .first()
        )

        if festival is None:
            raise ValueError("Festival introuvable")

        if festival.status == "published":
            raise ValueError(
                "Impossible de modifier le planning : "
                "le planning est déjà publié"
            )

        return festival

    # Vérifier les chevauchements entre concerts
    def _check_conflicts(
        self,
        festival_id,
        artist_id,
        stage_id,
        start_time,
        end_time,
        exclude_id=None
    ):
        concerts = (
            self.db.query(Concert)
            .filter(
                Concert.festival_id == festival_id,
                Concert.status != "cancelled"
            )
            .all()
        )

        for concert in concerts:
            if exclude_id is not None and concert.id == exclude_id:
                continue

            if overlaps(
                start_time,
                end_time,
                concert.start_time,
                concert.end_time
            ):
                if concert.stage_id == stage_id:
                    raise ValueError(
                        "Conflit : la scène est déjà occupée"
                    )

                if concert.artist_id == artist_id:
                    raise ValueError(
                        "Conflit : l'artiste est déjà programmé"
                    )

    # Vérifier les règles métier
    def _validate_concert(
        self,
        festival_id,
        artist_id,
        stage_id,
        start_time,
        end_time,
        exclude_id=None
    ):
        festival = (
            self.db.query(Festival)
            .filter(Festival.id == festival_id)
            .first()
        )

        artist = (
            self.db.query(Artist)
            .filter(Artist.id == artist_id)
            .first()
        )

        stage = (
            self.db.query(Stage)
            .filter(Stage.id == stage_id)
            .first()
        )

        if festival is None or artist is None or stage is None:
            raise ValueError(
                "Festival, artiste ou scène introuvable"
            )

        if stage.festival_id != festival.id:
            raise ValueError(
                "La scène n'appartient pas à ce festival"
            )

        if end_time <= start_time:
            raise ValueError(
                "La date de fin doit être postérieure à la date de début"
            )

        if (
            start_time < festival.start_date
            or end_time > festival.end_date
        ):
            raise ValueError(
                "Le concert doit se dérouler pendant le festival"
            )

        required = {
            equipment.strip()
            for equipment in (
                artist.required_equipment or ""
            ).split(",")
            if equipment.strip()
        }

        available = {
            equipment.strip()
            for equipment in (
                stage.available_equipment or ""
            ).split(",")
            if equipment.strip()
        }

        if not required.issubset(available):
            raise ValueError(
                "La scène ne dispose pas de tous les équipements requis"
            )

        self._check_conflicts(
            festival_id,
            artist_id,
            stage_id,
            start_time,
            end_time,
            exclude_id
        )

    # Créer un concert
    def create_concert(self, payload):

        # Empêcher la création après publication
        self._check_planning_status(payload.festival_id)

        self._validate_concert(
            payload.festival_id,
            payload.artist_id,
            payload.stage_id,
            payload.start_time,
            payload.end_time
        )

        concert = Concert(
            festival_id=payload.festival_id,
            artist_id=payload.artist_id,
            stage_id=payload.stage_id,
            start_time=payload.start_time,
            end_time=payload.end_time
        )

        return self.repo.create(concert)

    # Déplacer un concert
    def reschedule_concert(self, concert_id, payload):

        concert = self.repo.get(concert_id)

        if concert is None:
            return None

        # Empêcher la modification d'un planning publié
        self._check_planning_status(concert.festival_id)

        if concert.status == "cancelled":
            raise ValueError(
                "Impossible de déplacer un concert annulé"
            )

        # Vérifier toutes les règles métier
        self._validate_concert(
            concert.festival_id,
            concert.artist_id,
            concert.stage_id,
            payload.start_time,
            payload.end_time,
            exclude_id=concert.id
        )

        # Modifier les horaires
        concert.start_time = payload.start_time
        concert.end_time = payload.end_time

        # Enregistrer en base
        self.db.commit()
        self.db.refresh(concert)

        # Gérer l'échec éventuel de notification
        try:
            self.notifications.notify_schedule_change(
                concert.id,
                f"Concert déplacé au {concert.start_time.isoformat()}"
            )
        except Exception:
            logger.exception(
                "Échec de notification pour le concert %s",
                concert.id
            )

        return concert

    # Annuler un concert
    def cancel_concert(self, concert_id):

        concert = self.repo.get(concert_id)

        if concert is None:
            return None

        # Empêcher l'annulation après publication
        self._check_planning_status(concert.festival_id)

        if concert.status == "cancelled":
            raise ValueError("Le concert est déjà annulé")

        concert.status = "cancelled"

        self.db.commit()
        self.db.refresh(concert)

        return concert

    # Consulter le planning
    def get_schedule(self, festival_id):
        return self.list_concerts(festival_id)
