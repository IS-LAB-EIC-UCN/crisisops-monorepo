from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import (
    AssignmentStatus,
    PersonnelAssignment,
    Responder,
    Shift,
)

TABLAS = [Responder.__table__, Shift.__table__, PersonnelAssignment.__table__]
MOMENTO = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=TABLAS)
    with Session(engine) as session:
        # 1: Activo y en turno (DEBE APARECER)
        session.add(
            Responder(
                id=1,
                name="Brigadista Apto",
                badge_number="B-101",
                role="FIREFIGHTER",
                is_active=True,
            )
        )
        session.add(
            Shift(
                responder_id=1,
                start_time=datetime(2026, 11, 1, 8, 0, tzinfo=UTC),
                end_time=datetime(2026, 11, 1, 16, 0, tzinfo=UTC),
            )
        )

        # 2: En turno pero no disponible (is_active=False) (NO DEBE APARECER)
        session.add(
            Responder(
                id=2,
                name="Brigadista No Disponible",
                badge_number="B-102",
                role="PARAMEDIC",
                is_active=False,
            )
        )
        session.add(
            Shift(
                responder_id=2,
                start_time=datetime(2026, 11, 1, 8, 0, tzinfo=UTC),
                end_time=datetime(2026, 11, 1, 16, 0, tzinfo=UTC),
            )
        )

        # 3: Disponible pero fuera de turno (NO DEBE APARECER)
        session.add(
            Responder(
                id=3,
                name="Brigadista Fuera de Turno",
                badge_number="B-103",
                role="RESCUE",
                is_active=True,
            )
        )
        session.add(
            Shift(
                responder_id=3,
                start_time=datetime(2026, 11, 1, 18, 0, tzinfo=UTC),
                end_time=datetime(2026, 11, 1, 22, 0, tzinfo=UTC),
            )
        )

        # 4: Disponible y en turno, pero con asignación activa (NO DEBE APARECER)
        session.add(
            Responder(
                id=4,
                name="Brigadista Ocupado",
                badge_number="B-104",
                role="DRIVER",
                is_active=True,
            )
        )
        session.add(
            Shift(
                responder_id=4,
                start_time=datetime(2026, 11, 1, 8, 0, tzinfo=UTC),
                end_time=datetime(2026, 11, 1, 16, 0, tzinfo=UTC),
            )
        )
        session.add(
            PersonnelAssignment(
                responder_id=4,
                start_at=datetime(2026, 11, 1, 9, 0, tzinfo=UTC),
                end_at=datetime(2026, 11, 1, 12, 0, tzinfo=UTC),
                status=AssignmentStatus.ACTIVE,
            )
        )

        session.commit()
        yield session


@pytest.fixture()
def client(db):
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides = {get_db: lambda: db}
    yield TestClient(app)
    app.dependency_overrides = anteriores


def test_filtra_solo_personal_en_turno_y_disponible(client):
    """Criterio 1: muestra únicamente a quienes cumplen ambos criterios de forma simultánea."""
    response = client.get(
        "/api/v1/personnel/responders/available",
        params={"moment": MOMENTO.isoformat()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert [r["id"] for r in body["responders"]] == [1]
    assert body["responders"][0]["name"] == "Brigadista Apto"


def test_excluye_automaticamente_al_cambiar_a_no_disponible(client, db):
    """Criterio 2: al cambiar is_active a False, se excluye automáticamente del resultado."""
    brigadista = db.get(Responder, 1)
    assert brigadista is not None
    brigadista.is_active = False
    db.commit()

    response = client.get(
        "/api/v1/personnel/responders/available",
        params={"moment": MOMENTO.isoformat()},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["responders"] == []