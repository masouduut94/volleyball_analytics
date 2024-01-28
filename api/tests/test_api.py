import unittest

import pytest

from api.rest import app
from api.schemas import TeamData
from fastapi.testclient import TestClient
from api.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
client = TestClient(app)
app.dependency_overrides[get_db] = get_db


def test_get_main():
    # Base.metadata.create_all(bind=engine)
    response1 = client.get("http://127.0.0.1:8000/")
    assert response1.status_code == 200


def test_get_team():
    # Base.metadata.create_all(bind=engine)
    t: TeamData = TeamData(name='canada', is_national_team=True)
    response1 = client.post("http://127.0.0.1:8000/team/", json=t.dict())
    assert response1.status_code == 200
    f = response1.json()
    # nation = Nation.save(**n.model_dump())
    response = client.get(f"/team/{f.id}")
    assert response.status_code == 200


def test_get_all_teams():
    t = TeamData(name='canada', is_national_team=True)
    response1 = client.post(f"localhost:8000/team/", json=t.model_dump_json())
    assert response1.status_code == 200
    f = response1.json()
    response = client.get(f"localhost:8000/team/")
    assert response.status_code == 200
