import pytest
from fastapi.testclient import TestClient

from crisisops.core.exceptions import DomainError
from crisisops.main import app
from crisisops.modules.personnel.models import Certification
from crisisops.modules.personnel.router import get_personnel_service

client = TestClient(app)


class MockService:
    def add_skill_to_responder(self, responder_id: int, skill_code: str):
        if responder_id == 999:
            raise DomainError("El brigadista con ID 999 no existe.")
        if skill_code == "DUPLICATED":
            raise DomainError("La competencia DUPLICATED ya está asociada al brigadista.")
        return None

    def add_certification(self, responder_id: int, payload):
        if responder_id == 999:
            raise DomainError("El brigadista con ID 999 no existe.")
        return Certification(
            id=1,
            responder_id=responder_id,
            skill_code=payload.skill_code,
            issued_at=payload.issued_at,
            expires_at=payload.expires_at,
        )


@pytest.fixture(autouse=True)
def override_service():
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_personnel_service] = lambda: MockService()
    yield
    app.dependency_overrides = anteriores


def test_assign_skill_exitoso_retorna_201():
    response = client.post("/api/v1/personnel/responders/1/skills", json={"skill_code": "RESCUE"})
    assert response.status_code == 201


def test_assign_skill_persona_inexistente_retorna_404():
    response = client.post("/api/v1/personnel/responders/999/skills", json={"skill_code": "RESCUE"})
    assert response.status_code == 404


def test_assign_skill_duplicada_retorna_409():
    payload = {"skill_code": "DUPLICATED"}
    response = client.post("/api/v1/personnel/responders/1/skills", json=payload)
    assert response.status_code == 409


def test_create_certification_exitoso_retorna_201():
    payload = {
        "skill_code": "PARAMEDIC",
        "issued_at": "2026-11-01T10:00:00Z",
        "expires_at": "2026-11-10T10:00:00Z",
    }
    response = client.post("/api/v1/personnel/responders/1/certifications", json=payload)
    assert response.status_code == 201
    assert response.json()["skill_code"] == "PARAMEDIC"


def test_create_certification_fechas_invalidas_retorna_422():
    payload = {
        "skill_code": "PARAMEDIC",
        "issued_at": "2026-11-10T10:00:00Z",
        "expires_at": "2026-11-01T10:00:00Z",
    }
    response = client.post("/api/v1/personnel/responders/1/certifications", json=payload)
    assert response.status_code == 422


def test_create_certification_persona_inexistente_retorna_404():
    payload = {
        "skill_code": "PARAMEDIC",
        "issued_at": "2026-11-01T10:00:00Z",
        "expires_at": "2026-11-10T10:00:00Z",
    }
    response = client.post("/api/v1/personnel/responders/999/certifications", json=payload)
    assert response.status_code == 404
