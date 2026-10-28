from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import PersonnelAssignment, Responder


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=[Responder.__table__, PersonnelAssignment.__table__])
    with Session(engine) as session:
        session.add(Responder(id=1, name="Brigadista 1", badge_number="B-001", role="FIREFIGHTER"))
        session.commit()
        yield session


@pytest.fixture()
def client(db):
    anteriores = app.dependency_overrides.copy()  # guarda el mock de test_router.py
    app.dependency_overrides = {get_db: lambda: db}
    yield TestClient(app)
    app.dependency_overrides = anteriores


def asignar(client, inicio, fin):
    return client.post(
        "/api/v1/personnel/responders/1/assignments",
        json={"start_at": f"2026-11-01T{inicio}:00:00", "end_at": f"2026-11-01T{fin}:00:00"},
    )


def test_asignacion_sin_choque_se_crea(client):
    assert asignar(client, 10, 14).status_code == 201


def test_asignacion_que_se_solapa_es_rechazada(client):
    asignar(client, 10, 14)
    assert asignar(client, 12, 16).status_code == 422


def test_borde_exacto_no_es_choque(client):
    asignar(client, 10, 14)
    assert asignar(client, 14, 16).status_code == 201


def test_asignacion_cancelada_no_bloquea(client, db):
    db.add(PersonnelAssignment(
        responder_id=1,
        start_at=datetime(2026, 11, 1, 10),
        end_at=datetime(2026, 11, 1, 14),
        status="CANCELLED",
    ))
    db.commit()
    assert asignar(client, 12, 16).status_code == 201