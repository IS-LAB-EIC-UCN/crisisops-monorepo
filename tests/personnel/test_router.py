import pytest
from fastapi.testclient import TestClient

from crisisops.core.exceptions import DomainError
from crisisops.main import app
from crisisops.modules.personnel.router import get_personnel_service
from crisisops.modules.personnel.schemas import AssignmentCreate

client = TestClient(app)

class MockPersonnelService:
    """Mock del servicio para probar únicamente el comportamiento del router."""
    def create_assignment(self, responder_id: int, data: AssignmentCreate):
        if data.start_at >= data.end_at:
            raise ValueError("start debe ser anterior a end")
        
        # Simulamos que el ID 2 ya tiene un turno que se solapa
        if responder_id == 2:
            raise DomainError(
                f"El personal con ID {responder_id} ya posee una asignación activa que se solapa."
            )
        
        
        class MockAssignment:
            def __init__(self):
                self.id = 1
                self.responder_id = responder_id
                self.mission_id = data.mission_id
                self.start_at = data.start_at
                self.end_at = data.end_at
                self.status = "ACTIVE"
                
        return MockAssignment()


@pytest.fixture(autouse=True)
def usar_mock_service():
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_personnel_service] = lambda: MockPersonnelService()
    yield
    app.dependency_overrides = anteriores


def test_create_assignment_success():
    """Prueba la creación exitosa de una asignación (HTTP 201)."""
    payload = {
        "mission_id": 100,
        "start_at": "2026-11-01T10:00:00Z",
        "end_at": "2026-11-01T14:00:00Z"
    }
    response = client.post("/api/v1/personnel/responders/1/assignments", json=payload)
    
    assert response.status_code == 201
    assert response.json()["mission_id"] == 100
    assert response.json()["status"] == "ACTIVE"


def test_create_assignment_overlap_returns_422():
    """Prueba que un solapamiento retorne HTTP 422, según la historia de usuario."""
    payload = {
        "mission_id": 101,
        "start_at": "2026-11-01T12:00:00Z",
        "end_at": "2026-11-01T16:00:00Z"
    }
    # Usamos el ID 2 para disparar el DomainError configurado en el mock
    response = client.post("/api/v1/personnel/responders/2/assignments", json=payload)
    
    assert response.status_code == 422
    assert "se solapa" in response.json()["detail"]


def test_create_assignment_invalid_dates_returns_422():
    """Prueba que el envío de fechas invertidas retorne HTTP 422."""
    payload = {
        "mission_id": 102,
        "start_at": "2026-11-01T15:00:00Z",
        "end_at": "2026-11-01T10:00:00Z"  # El fin es anterior al inicio
    }
    response = client.post("/api/v1/personnel/responders/1/assignments", json=payload)
    
    assert response.status_code == 422
    assert "anterior" in response.json()["detail"]