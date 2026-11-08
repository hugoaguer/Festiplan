import pytest


@pytest.fixture
def scheduled_concert(client):
    festival_id = client.post(
        "/festivals",
        json={
            "name": "Incident Test Festival",
            "location": "Paris",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:00:00",
        },
    ).json()["id"]
    artist_id = client.post(
        "/artists",
        json={"name": "Incident Artist", "genre": "Metal", "required_equipment": []},
    ).json()["id"]
    stage_id = client.post(
        "/stages",
        json={
            "festival_id": festival_id,
            "name": "Incident Stage",
            "capacity": 100,
            "available_equipment": [],
        },
    ).json()["id"]
    concert = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": "2027-06-18T12:00:00",
            "end_time": "2027-06-18T13:00:00",
        },
    )
    assert concert.status_code == 201
    return concert.json()["id"]


def test_incident_requires_existing_concert(client):
    response = client.post(
        "/incidents",
        json={"concert_id": 999, "description": "Amplifier failure"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("description", ["", "   ", "\t\n"])
def test_incident_rejects_blank_description(client, scheduled_concert, description):
    response = client.post(
        "/incidents",
        json={"concert_id": scheduled_concert, "description": description},
    )

    assert response.status_code == 422


def test_incident_description_is_trimmed(client, scheduled_concert):
    response = client.post(
        "/incidents",
        json={"concert_id": scheduled_concert, "description": "  Cable failure  "},
    )

    assert response.status_code == 201
    assert response.json()["description"] == "Cable failure"


def test_incident_accepts_short_non_empty_description(client, scheduled_concert):
    response = client.post(
        "/incidents",
        json={"concert_id": scheduled_concert, "description": "OK"},
    )

    assert response.status_code == 201
    assert response.json()["description"] == "OK"
