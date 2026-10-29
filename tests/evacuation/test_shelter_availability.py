
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.evacuation.models import Shelter


TABLAS_EVACUACION = [Shelter.__table__]


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(
        bind=engine,
        tables=TABLAS_EVACUACION,
    )

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(
        bind=engine,
        tables=TABLAS_EVACUACION,
    )
    engine.dispose()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def refugio(db_session):
    nuevo_refugio = Shelter(
        name="Refugio de prueba",
        location="Coquimbo",
        capacity=50,
    )

    db_session.add(nuevo_refugio)
    db_session.commit()
    db_session.refresh(nuevo_refugio)

    return nuevo_refugio


def test_desactivar_refugio(client, refugio):
    respuesta = client.patch(
        f"/api/v1/evacuation/refugios/{refugio.id}/disponibilidad",
        json={"availability": "DISABLED"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["availability"] == "DISABLED"


def test_activar_refugio(client, db_session, refugio):
    refugio.availability = "DISABLED"
    db_session.commit()

    respuesta = client.patch(
        f"/api/v1/evacuation/refugios/{refugio.id}/disponibilidad",
        json={"availability": "ENABLED"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["availability"] == "ENABLED"


def test_refugio_inexistente(client):
    respuesta = client.patch(
        "/api/v1/evacuation/refugios/999999/disponibilidad",
        json={"availability": "DISABLED"},
    )

    assert respuesta.status_code == 404


def test_rechazar_disponibilidad_invalida(client, refugio):
    respuesta = client.patch(
        f"/api/v1/evacuation/refugios/{refugio.id}/disponibilidad",
        json={"availability": "INVENTADO"},
    )

    assert respuesta.status_code == 422


def test_disponibilidad_se_mantiene_guardada(client, db_session, refugio):
    respuesta = client.patch(
        f"/api/v1/evacuation/refugios/{refugio.id}/disponibilidad",
        json={"availability": "DISABLED"},
    )

    assert respuesta.status_code == 200

    # Consultamos de nuevo el refugio desde la sesión.
    db_session.expire_all()
    refugio_actualizado = db_session.get(type(refugio), refugio.id)

    assert refugio_actualizado is not None
    assert refugio_actualizado.availability == "DISABLED"

