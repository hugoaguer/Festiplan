from app.ports import NotificationDeliveryError
from app.utils.email_sender import send_email


class SimulatedNotificationAdapter:
    def notify_schedule_change(self, subject_id: int, message: str) -> None:
        try:
            send_email(
                "production@festiplan.test",
                f"Modification du concert #{subject_id}",
                message,
            )
        except RuntimeError as exc:
            raise NotificationDeliveryError(str(exc)) from exc
