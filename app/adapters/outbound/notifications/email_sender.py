
from app.bootstrap.config import settings


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Simulation locale : aucun e-mail réel n'est envoyé."""
    if settings.fail_notifications:
        raise RuntimeError(
            "Simulation : le service de notification est indisponible"
        )

    print(
        f"[FAKE EMAIL] to={recipient} "
        f"subject={subject} body={body}"
    )


class EmailNotificationSender:
    def notify_schedule_change(
        self,
        concert_id: int,
        message: str,
    ) -> None:
        send_email(
            recipient="production@festiplan.test",
            subject=f"Modification du concert #{concert_id}",
            body=message,
        )
