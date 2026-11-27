"""H04 - Casos límite del endpoint de personal disponible."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.personnel.models import PersonnelAssignment, Responder, Shift

URL = "/api/v1/personnel/responders/available"


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(
        engine,
        tables=[Responder.__table__, Shift.__table__, PersonnelAssignment.__table__],
    )
    with Session(engine) as db:
        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides = {get_db: lambda: db}
        yield TestClient(app)
        app.dependency_overrides = anteriores


def test_sin_personal_retorna_lista_vacia(client):
    response = client.get(URL, params={"moment": "2026-11-01T10:00:00Z"})

    assert response.status_code == 200
    assert response.json() == {"count": 0, "responders": []}


def test_fecha_invalida_retorna_422(client):
    response = client.get(URL, params={"moment": "no-es-una-fecha"})

    assert response.status_code == 422
