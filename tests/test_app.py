from fastapi.testclient import TestClient

from crisisops.main import app

client = TestClient(app)


def test_global_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_all_modules_are_wired() -> None:
    paths = [
        "/api/v1/emergencies/health",
        "/api/v1/resources/health",
        "/api/v1/personnel/health",
        "/api/v1/operations/health",
        "/api/v1/evacuation/health",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.json()["status"] == "ok"
