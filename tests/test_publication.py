from datetime import datetime

from app.database import SessionLocal
from app.models import Concert


def test_publish_unknown_festival_returns_404(client):
 assert client.post("/festivals/999/publish").status_code==404


def test_publish_rejects_invalid_schedule_and_keeps_preparation_status(client):
 festival_response = client.post("/festivals",json={
  "name":"Publish Validation Festival",
  "location":"Paris",
  "start_date":"2027-06-18T10:00:00",
  "end_date":"2027-06-20T23:00:00"
 })
 festival_id = festival_response.json()["id"]
 artist_one = client.post("/artists",json={
  "name":"Publish Artist One",
  "genre":"Metal",
  "required_equipment":[]
 }).json()["id"]
 artist_two = client.post("/artists",json={
  "name":"Publish Artist Two",
  "genre":"Metal",
  "required_equipment":[]
 }).json()["id"]
 stage_id = client.post("/stages",json={
  "festival_id":festival_id,
  "name":"Publish Stage",
  "capacity":100,
  "available_equipment":[]
 }).json()["id"]
 concert_response = client.post("/concerts",json={
  "festival_id":festival_id,
  "artist_id":artist_one,
  "stage_id":stage_id,
  "start_time":"2027-06-18T12:00:00",
  "end_time":"2027-06-18T13:00:00"
 })
 assert concert_response.status_code == 201

 db = SessionLocal()
 try:
  db.add(Concert(
   festival_id=festival_id,
   artist_id=artist_two,
   stage_id=stage_id,
   start_time=datetime.fromisoformat(concert_response.json()["start_time"]),
   end_time=datetime.fromisoformat("2027-06-18T12:30:00")
  ))
  db.commit()
 finally:
  db.close()

 response = client.post(f"/festivals/{festival_id}/publish")

 assert response.status_code == 400
 assert "scène est déjà occupée" in response.json()["detail"]
 festival = client.get("/festivals").json()[0]
 assert festival["status"] == "preparation"
