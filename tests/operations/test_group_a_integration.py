"""Pruebas de integración entre Operaciones (D) y Emergencias (A)."""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base, get_db
from crisisops.main import app
from crisisops.modules.emergencies.enums import EmergencyStatus, EmergencyType
from crisisops.modules.emergencies.models import Emergency
from crisisops.modules.operations.models import Operation

URL = "/api/v1/operations"
PAYLOAD = {"emergency_id": 1, "name": "Evacuación del edificio", "priority": "HIGH"}
INTEGRATION_TABLES = [Emergency.__table__, Operation.__table__]


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=INTEGRATION_TABLES)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine, tables=INTEGRATION_TABLES)
    engine.dispose()


@pytest.fixture()
def integration_client(db_session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def create_emergency(db_session: Session, status: EmergencyStatus) -> Emergency:
    emergency = Emergency(
        type=EmergencyType.FIRE,
        status=status,
        date_time=datetime.now(UTC),
        reported_by="operations-integration-test",
    )
    db_session.add(emergency)
    db_session.commit()
    return emergency


def operation_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Operation)) or 0


def test_active_emergency_from_group_a_creates_operation(
    integration_client: TestClient, db_session: Session
) -> None:
    emergency = create_emergency(db_session, EmergencyStatus.ACTIVE)

    response = integration_client.post(URL, json={**PAYLOAD, "emergency_id": emergency.id})

    assert response.status_code == 201
    assert operation_count(db_session) == 1
    saved = db_session.scalar(select(Operation))
    assert saved is not None
    assert saved.emergency_id == emergency.id


@pytest.mark.parametrize(
    "status",
    [EmergencyStatus.VALIDATED, EmergencyStatus.REJECTED],
)
def test_non_active_emergency_from_group_a_is_rejected(
    integration_client: TestClient,
    db_session: Session,
    status: EmergencyStatus,
) -> None:
    emergency = create_emergency(db_session, status)

    response = integration_client.post(URL, json={**PAYLOAD, "emergency_id": emergency.id})

    assert response.status_code == 409
    assert operation_count(db_session) == 0


def test_missing_emergency_from_group_a_is_rejected(
    integration_client: TestClient, db_session: Session
) -> None:
    response = integration_client.post(URL, json=PAYLOAD)

    assert response.status_code == 422
    assert operation_count(db_session) == 0


def test_group_a_database_failure_returns_503_and_rolls_back(
    integration_client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_get = db_session.get

    def fail_emergency_lookup(entity: type, ident: int, **kwargs: object) -> object:
        if entity is Emergency:
            raise OperationalError(
                "SELECT emergencies",
                {"id": ident},
                RuntimeError("database unavailable"),
            )
        return original_get(entity, ident, **kwargs)

    rollback = db_session.rollback
    rollback_calls = 0

    def track_rollback() -> None:
        nonlocal rollback_calls
        rollback_calls += 1
        rollback()

    monkeypatch.setattr(db_session, "get", fail_emergency_lookup)
    monkeypatch.setattr(db_session, "rollback", track_rollback)

    response = integration_client.post(URL, json=PAYLOAD)

    assert response.status_code == 503
    assert rollback_calls == 1
    assert operation_count(db_session) == 0
