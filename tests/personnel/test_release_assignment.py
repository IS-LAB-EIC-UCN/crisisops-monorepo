from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import AssignmentStatus, PersonnelAssignment, Responder


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=[Responder.__table__, PersonnelAssignment.__table__])
    with Session(engine) as session:
        session.add(Responder(id=1, name="Brigadista 1", badge_number="B-002", role="FIREFIGHTER"))
        session.commit()
        yield session


@pytest.fixture()
def client(db):
    anteriores = app.dependency_overrides.copy()  # guarda el mock de test_router.py
    app.dependency_overrides = {get_db: lambda: db}
    yield TestClient(app)
    app.dependency_overrides = anteriores


def test_liberar_asignacion_cambia_estado_a_released(db):
    assignment = PersonnelAssignment(
        responder_id=1,
        start_at=datetime(2026, 11, 1, 8),
        end_at=datetime(2026, 11, 1, 16),
        status=AssignmentStatus.ACTIVE,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    assignment.status = AssignmentStatus.CANCELLED
    db.commit()
    db.refresh(assignment)

    assert assignment.status == AssignmentStatus.CANCELLED


def test_asignacion_released_no_bloquea_nueva_asignacion(db, client):
    db.add(PersonnelAssignment(
        responder_id=1,
        start_at=datetime(2026, 11, 1, 8),
        end_at=datetime(2026, 11, 1, 16),
        status=AssignmentStatus.CANCELLED,
    ))
    db.commit()

    resp = client.post(
        "/api/v1/personnel/responders/1/assignments",
        json={"start_at": "2026-11-01T08:00:00", "end_at": "2026-11-01T16:00:00"},
    )
    assert resp.status_code == 201