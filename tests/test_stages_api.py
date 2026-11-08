import pytest


@pytest.mark.parametrize("capacity", [0, -1])
def test_stage_capacity_must_be_positive(client, capacity):
 r=client.post("/stages",json={
                                "festival_id":1,
                                "name":"Mainstage",
                                "capacity":capacity,
                                "available_equipment":[]
                               })
 assert r.status_code==422
