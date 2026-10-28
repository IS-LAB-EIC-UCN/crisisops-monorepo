"""Fixtures comunes de las pruebas del módulo operations (Grupo D)."""

from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.operations.models import (
    Mission,
    MissionPersonnelAssignment,
    MissionPersonnelRequirement,
    MissionResourceAssignment,
    MissionResourceRequirement,
    Operation,
)
from crisisops.modules.operations.repository import OperationsRepository
from crisisops.modules.operations.router import get_operations_service
from crisisops.modules.operations.service import OperationsService

# Solo se crean las tablas de este módulo; las de otros grupos no se tocan.
OPERATIONS_TABLES = [
    Operation.__table__,
    Mission.__table__,
    MissionResourceRequirement.__table__,
    MissionPersonnelRequirement.__table__,
    MissionResourceAssignment.__table__,
    MissionPersonnelAssignment.__table__,
]

# Estados de emergencia simulados de Grupo A. None = la emergencia no existe.
FAKE_EMERGENCIES: dict[int, str] = {
    1: "ACTIVE",
    2: "CLOSED",
    3: "REPORTED",
    4: "REJECTED",
}


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Sesión sobre una base SQLite en memoria, limpia en cada prueba."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=OPERATIONS_TABLES)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine, tables=OPERATIONS_TABLES)
    engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP de la app usando la base de pruebas."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class FakeEmergencyService:
    """Simula a Grupo A: devuelve el estado, None si no existe o falla si está caído."""

    def __init__(self, emergencies: dict[int, str]) -> None:
        self.emergencies = emergencies
        self.available = True

    def get_status(self, emergency_id: int) -> str | None:
        if not self.available:
            raise ConnectionError("Grupo A no disponible")
        return self.emergencies.get(emergency_id)


@pytest.fixture()
def emergency_service() -> FakeEmergencyService:
    return FakeEmergencyService(dict(FAKE_EMERGENCIES))


@pytest.fixture()
def get_emergency_status(
    emergency_service: FakeEmergencyService,
) -> Callable[[int], str | None]:
    """Función lista para pasar a OperationsService(get_emergency_status)."""
    return emergency_service.get_status


@pytest.fixture()
def api_client(
    client: TestClient,
    db_session: Session,
    get_emergency_status: Callable[[int], str | None],
) -> TestClient:
    """Cliente HTTP cuyo service consulta al Grupo A simulado en vez del real."""
    app.dependency_overrides[get_operations_service] = lambda: OperationsService(
        get_emergency_status, OperationsRepository(db_session)
    )
    return client


@pytest.fixture()
def operation_count(db_session: Session) -> Callable[[], int]:
    """Cuenta operaciones guardadas; sirve para probar que no se persistió nada."""
    return lambda: db_session.query(Operation).count()
