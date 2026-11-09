def test_create_incident_uses_default_timestamp_when_omitted(client):
    festival_response = client.post(
        "/festivals",
        json={
            "name": "Incident Test Festival",
            "location": "Bordeaux",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:00:00",
        },
    )
    assert festival_response.status_code == 201
    festival_id = festival_response.json()["id"]

    artist_response = client.post(
        "/artists",
        json={
            "name": "Incident Test Artist",
            "genre": "Metal",
            "required_equipment": [],
        },
    )
    assert artist_response.status_code == 201
    artist_id = artist_response.json()["id"]

    stage_response = client.post(
        "/stages",
        json={
            "festival_id": festival_id,
            "name": "Main Stage",
            "capacity": 1000,
            "available_equipment": [],
        },
    )
    assert stage_response.status_code == 201
    stage_id = stage_response.json()["id"]

    concert_response = client.post(
        "/concerts",
        json={
            "festival_id": festival_id,
            "artist_id": artist_id,
            "stage_id": stage_id,
            "start_time": "2027-06-18T15:00:00",
            "end_time": "2027-06-18T16:00:00",
        },
    )
    assert concert_response.status_code == 201
    concert_id = concert_response.json()["id"]

    response = client.post(
        "/incidents",
        json={
            "concert_id": concert_id,
            "description": "Un incident de test",
        },
    )

    assert response.status_code == 201
    assert response.json()["concert_id"] == concert_id
    assert response.json()["occurred_at"] is not None


def test_create_incident_rejects_unknown_concert(client):
    response = client.post(
        "/incidents",
        json={
            "concert_id": 999999,
            "description": "Un incident de test",
        },
    )

    assert response.status_code == 404
