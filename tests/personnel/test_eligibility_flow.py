
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import (
    Certification,
    PersonnelAssignment,
    Responder,
    ResponderSkill,
    Shift,
    Skill,
)

TABLAS = [Responder, Skill, ResponderSkill, Certification, Shift, PersonnelAssignment]


def h(hour, day=1):
    return datetime(2026, 11, day, hour)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=[t.__table__ for t in TABLAS])
    with Session(engine) as session:
        session.add(Skill(code="PARAMEDIC", name="Paramédico", requires_certification=True))
        session.add(Skill(code="DRIVER", name="Conductor", requires_certification=False))
        for rid in (1, 2, 3):
            session.add(
                Responder(id=rid, name=f"Brigadista {rid}", badge_number=f"B-{rid}", role="X")
            )
            session.add(Shift(responder_id=rid, start_time=h(8), end_time=h(20)))
        # 1: apto · 2: sin la skill · 3: certificación vencida
        session.add(ResponderSkill(responder_id=1, skill_code="PARAMEDIC"))
        session.add(ResponderSkill(responder_id=3, skill_code="PARAMEDIC"))
        session.add(ResponderSkill(responder_id=1, skill_code="DRIVER"))
        session.add(Certification(responder_id=1, skill_code="PARAMEDIC",
                                  issued_at=datetime(2026, 1, 1), expires_at=datetime(2027, 1, 1)))
        session.add(Certification(responder_id=3, skill_code="PARAMEDIC",
                                  issued_at=datetime(2025, 1, 1), expires_at=datetime(2026, 1, 1)))
        session.commit()
        yield session


@pytest.fixture()
def client(db):
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides = {get_db: lambda: db}
    yield TestClient(app)
    app.dependency_overrides = anteriores


def buscar(client, skill="PARAMEDIC"):
    return client.post(
        "/api/v1/personnel/responders/eligible",
        json={"start_time": "2026-11-01T10:00:00", "end_time": "2026-11-01T14:00:00",
              "required_skills": [skill]},
    )


def test_solo_aparece_el_brigadista_apto(client):
    response = buscar(client)
    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [1]


def test_brigadista_con_asignacion_solapada_no_aparece(client, db):
    db.add(PersonnelAssignment(responder_id=1, start_at=h(12), end_at=h(16), status="ACTIVE"))
    db.commit()
    assert buscar(client).json() == []


def test_skill_sin_certificacion_solo_trae_a_quien_la_tiene(client):
    assert [r["id"] for r in buscar(client, "DRIVER").json()] == [1]