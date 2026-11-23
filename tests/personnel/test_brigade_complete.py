"""T3.4 - Brigada que cubre todas las competencias requeridas es válida."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import Responder, ResponderSkill, Skill

URL = "/api/v1/personnel/brigades/validate"


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(
        engine, tables=[Responder.__table__, Skill.__table__, ResponderSkill.__table__]
    )
    with Session(engine) as session:
        session.add(Skill(code="PARAMEDIC", name="Paramédico", requires_certification=False))
        session.add(Skill(code="DRIVER", name="Conductor", requires_certification=False))
        session.add(Responder(id=1, name="Ana", badge_number="B-1", role="PARAMEDIC"))
        session.add(Responder(id=2, name="Beto", badge_number="B-2", role="DRIVER"))
        session.add(ResponderSkill(responder_id=1, skill_code="PARAMEDIC"))
        session.add(ResponderSkill(responder_id=2, skill_code="DRIVER"))
        session.commit()
        yield session


@pytest.fixture()
def client(db):
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides = {get_db: lambda: db}
    yield TestClient(app)
    app.dependency_overrides = anteriores


def test_brigada_completa_es_valida(client):
    response = client.post(
        URL, json={"responder_ids": [1, 2], "required_skills": ["PARAMEDIC", "DRIVER"]}
    )

    assert response.status_code == 200
    assert response.json() == {"is_valid": True, "missing_skills": []}


def test_lista_vacia_es_rechazada(client):
    response = client.post(URL, json={"responder_ids": [], "required_skills": ["PARAMEDIC"]})

    assert response.status_code == 422