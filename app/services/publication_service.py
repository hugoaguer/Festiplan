
import logging

from sqlalchemy.orm import Session

from app.models import Festival
from app.services.notification_service import NotificationService
from app.services.scheduling_service import SchedulingService


logger = logging.getLogger(__name__)


class PublicationService:

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService()
        self.scheduling = SchedulingService(db)

    def publish(self, festival_id):
        festival = (
            self.db.query(Festival)
            .filter(Festival.id == festival_id)
            .first()
        )

        if festival is None:
            return None

        if festival.status == "published":
            raise ValueError("Le planning est déjà publié")

        # Vérifier tous les concerts avant publication
        concerts = self.scheduling.list_concerts(festival_id)

        for concert in concerts:
            if concert.status == "cancelled":
                continue

            self.scheduling._validate_concert(
                concert.festival_id,
                concert.artist_id,
                concert.stage_id,
                concert.start_time,
                concert.end_time,
                exclude_id=concert.id
            )

        # Publier uniquement si les vérifications sont réussies
        festival.status = "published"

        self.db.commit()
        self.db.refresh(festival)

        # La notification est secondaire
        try:
            self.notifications.notify_schedule_change(
                festival_id,
                f"Le planning du festival {festival.name} a été publié."
            )
        except Exception:
            logger.exception(
                "Échec de notification du festival %s",
                festival_id
            )

        return festival
