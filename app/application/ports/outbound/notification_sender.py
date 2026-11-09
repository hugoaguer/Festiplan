
from typing import Protocol


class NotificationSenderPort(Protocol):
    def notify_schedule_change(
        self,
        concert_id: int,
        message: str,
    ) -> None:
        ...
