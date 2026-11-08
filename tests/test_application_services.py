from datetime import datetime

import pytest

from app.domain.entities import Artist, Concert, Festival, FestivalStatus, Incident, Stage
from app.ports import NotificationDeliveryError
from app.services.incident_service import IncidentService
from app.services.scheduling_service import SchedulingService


class MemoryFestivals:
    def __init__(self, *items: Festival) -> None:
        self.items = {item.id: item for item in items}

    def get(self, festival_id: int) -> Festival | None:
        return self.items.get(festival_id)

    def list(self):
        return list(self.items.values())

    def create(self, festival: Festival) -> Festival:
        festival.id = max(self.items, default=0) + 1
        self.items[festival.id] = festival
        return festival

    def save(self, festival: Festival) -> Festival:
        self.items[festival.id] = festival
        return festival


class MemoryArtists:
    def __init__(self, *items: Artist) -> None:
        self.items = {item.id: item for item in items}

    def get(self, artist_id: int) -> Artist | None:
        return self.items.get(artist_id)

    def list(self):
        return list(self.items.values())

    def create(self, artist: Artist) -> Artist:
        artist.id = max(self.items, default=0) + 1
        self.items[artist.id] = artist
        return artist


class MemoryStages:
    def __init__(self, *items: Stage) -> None:
        self.items = {item.id: item for item in items}

    def get(self, stage_id: int) -> Stage | None:
        return self.items.get(stage_id)

    def list_for_festival(self, festival_id: int):
        return [stage for stage in self.items.values() if stage.festival_id == festival_id]

    def create(self, stage: Stage) -> Stage:
        stage.id = max(self.items, default=0) + 1
        self.items[stage.id] = stage
        return stage


class MemoryConcerts:
    def __init__(self, *items: Concert) -> None:
        self.items = {item.id: item for item in items}

    def get(self, concert_id: int) -> Concert | None:
        return self.items.get(concert_id)

    def list_for_festival(self, festival_id: int):
        return [
            concert
            for concert in self.items.values()
            if concert.festival_id == festival_id and concert.status != "cancelled"
        ]

    def list_active(self):
        return [
            concert
            for concert in self.items.values()
            if concert.status != "cancelled"
        ]

    def create(self, concert: Concert) -> Concert:
        concert.id = max(self.items, default=0) + 1
        self.items[concert.id] = concert
        return concert

    def save(self, concert: Concert) -> Concert:
        self.items[concert.id] = concert
        return concert


class MemoryIncidents:
    def __init__(self) -> None:
        self.items: list[Incident] = []

    def list_for_concert(self, concert_id: int | None):
        if concert_id is None:
            return self.items
        return [item for item in self.items if item.concert_id == concert_id]

    def create(self, incident: Incident) -> Incident:
        incident.id = len(self.items) + 1
        self.items.append(incident)
        return incident


class MemoryNotifications:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.messages: list[tuple[int, str]] = []

    def notify_schedule_change(self, subject_id: int, message: str) -> None:
        self.messages.append((subject_id, message))
        if self.fail:
            raise NotificationDeliveryError("notification indisponible")


@pytest.fixture
def scheduling_setup():
    festival = Festival(
        1,
        "Festival",
        "Paris",
        datetime(2027, 6, 18),
        datetime(2027, 6, 20),
    )
    artist = Artist(1, "Groupe", "Metal")
    stage = Stage(1, 1, "Main", 1000)
    concert = Concert(
        1,
        1,
        1,
        1,
        datetime(2027, 6, 18, 12),
        datetime(2027, 6, 18, 13),
    )
    festivals = MemoryFestivals(festival)
    artists = MemoryArtists(artist)
    stages = MemoryStages(stage)
    concerts = MemoryConcerts(concert)
    notifications = MemoryNotifications()
    service = SchedulingService(
        concerts, festivals, artists, stages, notifications
    )
    return service, concerts, festivals, notifications


def test_scheduling_service_reschedules_without_database(scheduling_setup):
    service, concerts, _, notifications = scheduling_setup

    result = service.reschedule_concert(
        1, datetime(2027, 6, 18, 14), datetime(2027, 6, 18, 15)
    )

    assert result is not None
    concert, notification_sent = result
    assert notification_sent is True
    assert concerts.get(1).start_time == datetime(2027, 6, 18, 14)
    assert notifications.messages[0][0] == 1


def test_scheduling_service_rejects_conflict_without_database(scheduling_setup):
    service, concerts, _, _ = scheduling_setup
    concerts.create(
        Concert(
            None,
            1,
            2,
            1,
            datetime(2027, 6, 18, 14),
            datetime(2027, 6, 18, 15),
        )
    )

    with pytest.raises(ValueError, match="scène"):
        service.reschedule_concert(
            1, datetime(2027, 6, 18, 14, 30), datetime(2027, 6, 18, 15, 30)
        )


def test_notification_failure_does_not_undo_application_change(scheduling_setup):
    service, concerts, _, notifications = scheduling_setup
    notifications.fail = True

    result = service.reschedule_concert(
        1, datetime(2027, 6, 18, 14), datetime(2027, 6, 18, 15)
    )

    assert result is not None
    concert, notification_sent = result
    assert concert.start_time == datetime(2027, 6, 18, 14)
    assert concerts.get(1).start_time == datetime(2027, 6, 18, 14)
    assert notification_sent is False


def test_scheduling_service_rejects_changes_to_published_festival(scheduling_setup):
    service, _, festivals, _ = scheduling_setup
    festivals.items[1].status = FestivalStatus.PUBLISHED

    with pytest.raises(ValueError, match="publié"):
        service.reschedule_concert(
            1, datetime(2027, 6, 18, 14), datetime(2027, 6, 18, 15)
        )


def test_incident_service_validates_and_persists_with_ports():
    concerts = MemoryConcerts(
        Concert(
            1,
            1,
            1,
            1,
            datetime(2027, 6, 18, 12),
            datetime(2027, 6, 18, 13),
        )
    )
    incidents = MemoryIncidents()
    service = IncidentService(concerts, incidents)

    incident = service.create_incident(1, "  Panne lumière  ", None)

    assert incident is not None
    assert incident.description == "Panne lumière"
    assert incidents.list_for_concert(1) == [incident]


def test_incident_service_rejects_missing_concert_and_blank_description():
    service = IncidentService(MemoryConcerts(), MemoryIncidents())

    assert service.create_incident(10, "Incident", None) is None
    with pytest.raises(ValueError, match="vide"):
        service.create_incident(10, "  ", None)
