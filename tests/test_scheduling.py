import pytest

from app.config import settings


def create_festival(client):
    response = client.post(
        "/festivals",
        json={
            "name": "Festival Test",
            "location": "Paris",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:00:00",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_artist(client, name):
    response = client.post(
        "/artists",
        json={"name": name, "genre": "Metal", "required_equipment": []},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_stage(client, festival_id, name):
    response = client.post(
        "/stages",
        json={
            "festival_id": festival_id,
            "name": name,
            "capacity": 1000,
            "available_equipment": [],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_concert(client, festival_id, artist_id, stage_id, start, end):
    response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": start,
            "end_time": end,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def reschedule(client, concert_id, start, end):
    return client.patch(
        f"/concerts/{concert_id}/reschedule",
        json={"start_time": start, "end_time": end},
    )


def test_create_concert_rejects_missing_references(client):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Reference Artist")
    stage_id = create_stage(client, festival_id, "Reference Stage")
    valid_payload = {
        "festival_id": festival_id,
        "artist_id": artist_id,
        "stage_id": stage_id,
        "start_time": "2027-06-18T12:00:00",
        "end_time": "2027-06-18T13:00:00",
    }

    for reference, missing_id in (
        ("festival_id", 999),
        ("artist_id", 999),
        ("stage_id", 999),
    ):
        payload = {**valid_payload, reference: missing_id}
        assert client.post("/concerts", json=payload).status_code == 400


def test_create_concert_rejects_stage_from_another_festival(client):
    festival_id = create_festival(client)
    other_festival_id = client.post(
        "/festivals",
        json={
            "name": "Other Festival",
            "location": "Lyon",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:00:00",
        },
    ).json()["id"]
    artist_id = create_artist(client, "Foreign Stage Artist")
    stage_id = create_stage(client, other_festival_id, "Foreign Stage")

    response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": "2027-06-18T12:00:00",
            "end_time": "2027-06-18T13:00:00",
        },
    )

    assert response.status_code == 400
    assert "n'appartient pas" in response.json()["detail"]


def test_create_concert_requires_artist_equipment_on_stage(client):
    festival_id = create_festival(client)
    artist_response = client.post(
        "/artists",
        json={
            "name": "Rigging Artist",
            "genre": "Metal",
            "required_equipment": ["rigging"],
        },
    )
    artist_id = artist_response.json()["id"]
    stage_id = create_stage(client, festival_id, "Stage Without Rigging")

    response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": "2027-06-18T12:00:00",
            "end_time": "2027-06-18T13:00:00",
        },
    )

    assert response.status_code == 400
    assert "équipements requis" in response.json()["detail"]


@pytest.mark.parametrize(
    ("start_time", "end_time"),
    [
        ("2027-06-18T09:00:00", "2027-06-18T10:30:00"),
        ("2027-06-20T22:30:00", "2027-06-21T00:30:00"),
    ],
)
def test_create_concert_must_fit_festival_period(client, start_time, end_time):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Festival Window Artist")
    stage_id = create_stage(client, festival_id, "Festival Window Stage")

    response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": start_time,
            "end_time": end_time,
        },
    )

    assert response.status_code == 400
    assert "pendant le festival" in response.json()["detail"]


def test_reschedule_rejects_overlap_on_same_stage(client):
    festival_id = create_festival(client)
    first_artist = create_artist(client, "First Artist")
    second_artist = create_artist(client, "Second Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        first_artist,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    create_concert(
        client,
        festival_id,
        second_artist,
        stage_id,
        "2027-06-18T14:00:00",
        "2027-06-18T15:00:00",
    )

    response = reschedule(
        client, concert_id, "2027-06-18T13:30:00", "2027-06-18T14:30:00"
    )

    assert response.status_code == 400


def test_reschedule_rejects_artist_overlap_across_stages(client):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Shared Artist")
    first_stage = create_stage(client, festival_id, "Main Stage")
    second_stage = create_stage(client, festival_id, "Second Stage")
    concert_id = create_concert(
        client,
        festival_id,
        artist_id,
        first_stage,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    create_concert(
        client,
        festival_id,
        artist_id,
        second_stage,
        "2027-06-18T14:00:00",
        "2027-06-18T15:00:00",
    )

    response = reschedule(
        client, concert_id, "2027-06-18T13:30:00", "2027-06-18T14:30:00"
    )

    assert response.status_code == 400


def test_reschedule_rejects_artist_overlap_across_festivals(client):
    first_festival = create_festival(client)
    second_festival = client.post(
        "/festivals",
        json={
            "name": "Other Festival",
            "location": "Lyon",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:00:00",
        },
    ).json()["id"]
    artist_id = create_artist(client, "Touring Artist")
    first_stage = create_stage(client, first_festival, "First Stage")
    second_stage = create_stage(client, second_festival, "Second Stage")
    concert_id = create_concert(
        client,
        first_festival,
        artist_id,
        first_stage,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    create_concert(
        client,
        second_festival,
        artist_id,
        second_stage,
        "2027-06-18T14:00:00",
        "2027-06-18T15:00:00",
    )

    response = reschedule(
        client, concert_id, "2027-06-18T13:30:00", "2027-06-18T14:30:00"
    )

    assert response.status_code == 400


def test_reschedule_accepts_valid_move(client):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Moving Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        artist_id,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )

    response = reschedule(
        client, concert_id, "2027-06-18T14:00:00", "2027-06-18T15:00:00"
    )

    assert response.status_code == 200
    assert response.json()["start_time"] == "2027-06-18T14:00:00"


def test_reschedule_allows_back_to_back_concerts(client):
    festival_id = create_festival(client)
    first_artist = create_artist(client, "First Back-to-back Artist")
    second_artist = create_artist(client, "Second Back-to-back Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        first_artist,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    create_concert(
        client,
        festival_id,
        second_artist,
        stage_id,
        "2027-06-18T14:00:00",
        "2027-06-18T15:00:00",
    )

    response = reschedule(
        client, concert_id, "2027-06-18T13:00:00", "2027-06-18T14:00:00"
    )

    assert response.status_code == 200


def test_reschedule_is_rejected_after_publication(client):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Published Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        artist_id,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    assert client.post(f"/festivals/{festival_id}/publish").status_code == 200

    response = reschedule(
        client, concert_id, "2027-06-18T14:00:00", "2027-06-18T15:00:00"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Le planning publié ne peut pas être modifié"


def test_create_and_cancel_are_rejected_after_publication(client):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Locked Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        artist_id,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    assert client.post(f"/festivals/{festival_id}/publish").status_code == 200

    create_response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": create_artist(client, "New Artist"),
            "stage_id": stage_id,
            "start_time": "2027-06-18T14:00:00",
            "end_time": "2027-06-18T15:00:00",
        },
    )
    cancel_response = client.post(f"/concerts/{concert_id}/cancel")

    assert create_response.status_code == 400
    assert cancel_response.status_code == 400


def test_notification_failure_does_not_report_persisted_move_as_failed(client, monkeypatch):
    festival_id = create_festival(client)
    artist_id = create_artist(client, "Notification Artist")
    stage_id = create_stage(client, festival_id, "Main Stage")
    concert_id = create_concert(
        client,
        festival_id,
        artist_id,
        stage_id,
        "2027-06-18T12:00:00",
        "2027-06-18T13:00:00",
    )
    monkeypatch.setattr(settings, "fail_notifications", True)

    response = reschedule(
        client, concert_id, "2027-06-18T14:00:00", "2027-06-18T15:00:00"
    )

    assert response.status_code == 200
    assert response.headers["x-notification-status"] == "failed"
    persisted = client.get(f"/concerts/{concert_id}")
    assert persisted.status_code == 200
    assert persisted.json()["start_time"] == "2027-06-18T14:00:00"
