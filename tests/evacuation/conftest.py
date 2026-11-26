import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.evacuation.models import (
    EvacuationOrder,
    PeopleMovement,
    Shelter,
    ShelterAdmission,
)

TABLAS_EVACUACION = [
    EvacuationOrder.__table__,
    Shelter.__table__,
    PeopleMovement.__table__,
    ShelterAdmission.__table__,
]


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=TABLAS_EVACUACION)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine, tables=TABLAS_EVACUACION)


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def crear_refugio(db_session):
    def _crear(capacidad: int = 10, ocupacion: int = 0, estado: str = "OPEN") -> Shelter:
        refugio = Shelter(
            name="Refugio de prueba",
            location="Zona ficticia",
            capacity=capacidad,
            current_occupancy=ocupacion,
            status=estado,
        )
        db_session.add(refugio)
        db_session.commit()
        return refugio

    return _crear


@pytest.fixture()
def crear_admision(db_session):
    def _crear(
        refugio: Shelter, personas: int = 1, codigo: str = "CIV-001", estado: str = "ACTIVE"
    ) -> ShelterAdmission:
        admision = ShelterAdmission(
            shelter_id=refugio.id, evacuee_code=codigo, people_count=personas, status=estado
        )
        db_session.add(admision)
        db_session.commit()
        return admision

    return _crear
