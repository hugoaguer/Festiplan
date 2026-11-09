
import logging

from app.application.ports.outbound.concert_repository_port import ConcertRepositoryPort
from app.application.ports.outbound.festival_repository_port import FestivalRepositoryPort
from app.application.ports.outbound.artist_repository_port import ArtistRepositoryPort
from app.application.ports.outbound.stage_repository_port import StageRepositoryPort

from app.application.use_cases.create_concert import CreateConcertUseCase
from app.application.use_cases.reschedule_concert import RescheduleConcertUseCase
from app.application.use_cases.cancel_concert import CancelConcertUseCase

from app.services.notification_service import NotificationService


logger = logging.getLogger(__name__)


class SchedulingService:

    def __init__(
        self,
        db=None,
        repo: ConcertRepositoryPort | None = None,
        notifications: NotificationService | None = None,
        festival_repo: FestivalRepositoryPort | None = None,
        artist_repo: ArtistRepositoryPort | None = None,
        stage_repo: StageRepositoryPort | None = None,
    ):
        if (
            repo is None
            or festival_repo is None
            or artist_repo is None
            or stage_repo is None
        ):
            if db is None:
                raise ValueError(
                    "Une session ou les repositories sont nÃ©cessaires"
                )

            from app.repositories.concert_repository import ConcertRepository
            from app.repositories.festival_repository import FestivalRepository
            from app.repositories.artist_repository import ArtistRepository
            from app.repositories.stage_repository import StageRepository

            repo = repo if repo is not None else ConcertRepository(db)
            festival_repo = (
                festival_repo if festival_repo is not None
                else FestivalRepository(db)
            )
            artist_repo = (
                artist_repo if artist_repo is not None
                else ArtistRepository(db)
            )
            stage_repo = (
                stage_repo if stage_repo is not None
                else StageRepository(db)
            )

        self.repo = repo
        self.festival_repo = festival_repo
        self.artist_repo = artist_repo
        self.stage_repo = stage_repo
        self.notifications = (
            notifications if notifications is not None
            else NotificationService()
        )

    def list_concerts(self, festival_id):
        return self.repo.list_for_festival(festival_id)

    def get_concert(self, concert_id):
        return self.repo.get(concert_id)

    def create_concert(self, payload):
        use_case = CreateConcertUseCase(
            concert_repo=self.repo,
            festival_repo=self.festival_repo,
            artist_repo=self.artist_repo,
            stage_repo=self.stage_repo,
        )

        return use_case.execute(
            festival_id=payload.festival_id,
            artist_id=payload.artist_id,
            stage_id=payload.stage_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )

    def reschedule_concert(self, concert_id, payload):
        use_case = RescheduleConcertUseCase(
            concert_repo=self.repo,
            festival_repo=self.festival_repo,
            artist_repo=self.artist_repo,
            stage_repo=self.stage_repo,
        )

        concert = use_case.execute(
            concert_id=concert_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )

        if concert is None:
            return None

        try:
            self.notifications.notify_schedule_change(
                concert.id,
                f"Concert dÃ©placÃ© au {concert.start_time.isoformat()}",
            )
        except Exception:
            logger.exception(
                "Ã‰chec de notification pour le concert %s",
                concert.id,
            )

        return concert

    def cancel_concert(self, concert_id):
        use_case = CancelConcertUseCase(
            concert_repo=self.repo,
            festival_repo=self.festival_repo,
        )

        return use_case.execute(concert_id)

    def get_schedule(self, festival_id):
        return self.list_concerts(festival_id)
