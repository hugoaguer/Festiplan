from datetime import datetime

import pytest

from app.domain.entities import Festival, FestivalStatus
from app.domain.scheduling import (
    InvalidScheduleError,
    InvalidTimeSlotError,
    ScheduledConcert,
    SchedulingConflictError,
    TimeSlot,
    validate_concert_assignment,
    validate_capacity,
    validate_full_schedule,
    validate_incident_description,
    ensure_no_conflicts,
)


def scheduled_concert(
    concert_id=1,
    festival_id=1,
    artist_id=1,
    stage_id=10,
    stage_festival_id=1,
    start_hour=12,
    end_hour=13,
    festival_start_hour=10,
    festival_end_hour=23,
    required_equipment=frozenset(),
    available_equipment=frozenset(),
):
    day = datetime(2027, 6, 18)
    return ScheduledConcert(
        concert_id=concert_id,
        festival_id=festival_id,
        artist_id=artist_id,
        stage_id=stage_id,
        stage_festival_id=stage_festival_id,
        time_slot=TimeSlot(
            day.replace(hour=start_hour), day.replace(hour=end_hour)
        ),
        festival_start=day.replace(hour=festival_start_hour),
        festival_end=day.replace(hour=festival_end_hour),
        required_equipment=required_equipment,
        available_equipment=available_equipment,
    )


def test_time_slot_requires_end_after_start():
    start = datetime(2027, 6, 18, 12)

    with pytest.raises(InvalidTimeSlotError):
        TimeSlot(start, start)


def test_time_slots_that_only_touch_at_boundary_do_not_overlap():
    first = TimeSlot(datetime(2027, 6, 18, 12), datetime(2027, 6, 18, 13))
    second = TimeSlot(datetime(2027, 6, 18, 13), datetime(2027, 6, 18, 14))

    assert not first.overlaps(second)


@pytest.mark.parametrize(
    ("candidate_artist", "candidate_stage", "other_artist", "other_stage"),
    [(1, 10, 2, 10), (1, 10, 1, 11)],
)
def test_conflicts_reject_shared_stage_or_artist(
    candidate_artist, candidate_stage, other_artist, other_stage
):
    candidate = scheduled_concert(artist_id=candidate_artist, stage_id=candidate_stage)
    other = scheduled_concert(
        concert_id=2,
        artist_id=other_artist,
        stage_id=other_stage,
        start_hour=12,
        end_hour=14,
    )

    with pytest.raises(SchedulingConflictError):
        ensure_no_conflicts(candidate, [other])


def test_assignment_requires_stage_from_same_festival():
    with pytest.raises(InvalidScheduleError, match="n'appartient pas"):
        validate_concert_assignment(scheduled_concert(stage_festival_id=2))


@pytest.mark.parametrize(
    ("start_hour", "end_hour", "festival_end_hour"),
    [(9, 10, 23), (22, 23, 22)],
)
def test_assignment_must_fit_festival_period(start_hour, end_hour, festival_end_hour):
    with pytest.raises(InvalidScheduleError, match="pendant le festival"):
        validate_concert_assignment(
            scheduled_concert(
                start_hour=start_hour,
                end_hour=end_hour,
                festival_end_hour=festival_end_hour,
            )
        )


def test_assignment_requires_all_artist_equipment():
    concert = scheduled_concert(
        required_equipment=frozenset({"lights", "rigging"}),
        available_equipment=frozenset({"lights"}),
    )

    with pytest.raises(InvalidScheduleError, match="équipements requis"):
        validate_concert_assignment(concert)


def test_full_schedule_rejects_overlapping_concerts():
    first = scheduled_concert()
    second = scheduled_concert(
        concert_id=2,
        artist_id=2,
        start_hour=12,
        end_hour=14,
    )

    with pytest.raises(SchedulingConflictError):
        validate_full_schedule([first, second])


@pytest.mark.parametrize("capacity", [0, -1])
def test_capacity_must_be_positive(capacity):
    with pytest.raises(ValueError, match="strictement positive"):
        validate_capacity(capacity)


def test_festival_schedule_transitions_from_preparation_to_published():
    festival = Festival(
        1,
        "Festival",
        "Paris",
        datetime(2027, 6, 18),
        datetime(2027, 6, 20),
    )

    festival.publish_schedule()

    assert festival.status is FestivalStatus.PUBLISHED
    with pytest.raises(ValueError, match="Seul un planning en préparation"):
        festival.publish_schedule()


def test_published_festival_schedule_cannot_be_modified():
    festival = Festival(
        1,
        "Festival",
        "Paris",
        datetime(2027, 6, 18),
        datetime(2027, 6, 20),
        status=FestivalStatus.PUBLISHED,
    )

    with pytest.raises(ValueError, match="planning publié"):
        festival.ensure_schedule_is_editable()


@pytest.mark.parametrize("description", ["", "   ", "\t\n"])
def test_incident_description_must_not_be_blank(description):
    with pytest.raises(ValueError, match="ne peut pas être vide"):
        validate_incident_description(description)


def test_incident_description_is_trimmed():
    assert validate_incident_description("  câble débranché  ") == "câble débranché"
