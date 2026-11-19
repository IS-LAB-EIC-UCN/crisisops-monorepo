import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import Responder, ResponderSkill, Skill

TABLAS = [Responder, Skill, ResponderSkill]
URL = "/api/v1/personnel/brigades/validate"


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=[t.__table__ for t in TABLAS])
    with Session(engine) as session:
        session.add(Skill(code="PARAMEDIC", name="Paramédico", requires_certification=False))
        session.add(Skill(code="DRIVER", name="Conductor", requires_certification=False))
        session.add(Skill(code="RESCUE", name="Rescatista", requires_certification=False))
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


def validar(client, responder_ids, required_skills):
    return client.post(
        URL, json={"responder_ids": responder_ids, "required_skills": required_skills}
    )


def test_brigada_con_una_competencia_faltante_retorna_422(client):
    response = validar(client, [1, 2], ["PARAMEDIC", "RESCUE"])

    assert response.status_code == 422
    resultado = response.json()["detail"]
    assert resultado["is_valid"] is False
    assert resultado["missing_skills"] == ["RESCUE"]


def test_competencias_cubiertas_no_aparecen_como_faltantes(client):
    response = validar(client, [1, 2], ["PARAMEDIC", "DRIVER", "RESCUE"])

    assert response.status_code == 422
    faltantes = response.json()["detail"]["missing_skills"]
    assert "PARAMEDIC" not in faltantes
    assert "DRIVER" not in faltantes
    assert faltantes == ["RESCUE"]


def test_brigada_con_varias_competencias_faltantes_las_identifica_todas(client):
    response = validar(client, [1], ["PARAMEDIC", "DRIVER", "RESCUE"])

    assert response.status_code == 422
    assert sorted(response.json()["detail"]["missing_skills"]) == ["DRIVER", "RESCUE"]
