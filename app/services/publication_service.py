
import logging

from app.application.use_cases.publish_festival import PublishFestivalUseCase
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort
from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort
from app.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class PublicationService:

    def __init__(
        self,
        festival_repo: FestivalRepositoryPort,
        concert_repo: ConcertRepositoryPort,
        artist_repo: ArtistRepositoryPort,
        stage_repo: StageRepositoryPort,
        notifications: NotificationService | None = None,
    ):
        self.festival_repo = festival_repo
        self.concert_repo = concert_repo
        self.artist_repo = artist_repo
        self.stage_repo = stage_repo
        self.notifications = (
            notifications if notifications is not None
            else NotificationService()
        )

    def publish(self, festival_id):
        use_case = PublishFestivalUseCase(
            festival_repo=self.festival_repo,
            concert_repo=self.concert_repo,
            artist_repo=self.artist_repo,
            stage_repo=self.stage_repo,
        )

        festival = use_case.execute(festival_id)

        if festival is None:
            return None

        try:
            self.notifications.notify_schedule_change(
                festival_id,
                f"Le planning du festival {festival.name} a Ã©tÃ© publiÃ©."
            )

        except Exception:
            logger.exception(
                "Ã‰chec de notification du festival %s",
                festival_id,
            )

        return festival
