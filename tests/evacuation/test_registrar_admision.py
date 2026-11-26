"""Pruebas para impedir admisiones cuando un refugio no tiene capacidad."""

from crisisops.modules.evacuation.models import Shelter, ShelterAdmission


def url(refugio_id: int) -> str:
    return f"/api/v1/evacuation/shelters/{refugio_id}/admissions"


def recargar(db_session, refugio: Shelter):
    db_session.expire_all()
    return db_session.get(Shelter, refugio.id)


def test_admision_actualiza_la_ocupacion(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=5, ocupacion=2)

    response = client.post(
        url(refugio.id),
        json={"evacuee_code": "CIV-001", "people_count": 2},
    )

    assert response.status_code == 201
    assert response.json()["people_count"] == 2
    refugio = recargar(db_session, refugio)
    assert refugio.current_occupancy == 4
    assert refugio.status == "OPEN"


def test_admision_llena_el_refugio(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=5, ocupacion=3)

    response = client.post(
        url(refugio.id),
        json={"evacuee_code": "CIV-001", "people_count": 2},
    )

    assert response.status_code == 201
    refugio = recargar(db_session, refugio)
    assert refugio.current_occupancy == 5
    assert refugio.status == "FULL"


def test_no_permite_superar_capacidad(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=3, ocupacion=2)

    response = client.post(
        url(refugio.id),
        json={"evacuee_code": "CIV-001", "people_count": 2},
    )

    assert response.status_code == 409
    assert "cupos" in response.json()["detail"].lower()
    refugio = recargar(db_session, refugio)
    assert refugio.current_occupancy == 2
    assert db_session.query(ShelterAdmission).count() == 0


def test_refugio_inexistente_responde_404(client):
    response = client.post(
        url(999),
        json={"evacuee_code": "CIV-001", "people_count": 1},
    )

    assert response.status_code == 404


def test_datos_de_admision_invalidos_responden_422(client, crear_refugio):
    refugio = crear_refugio()

    sin_codigo = client.post(url(refugio.id), json={"people_count": 1})
    personas_invalidas = client.post(
        url(refugio.id),
        json={"evacuee_code": "CIV-001", "people_count": 0},
    )

    assert sin_codigo.status_code == 422
    assert personas_invalidas.status_code == 422
