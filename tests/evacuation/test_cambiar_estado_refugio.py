import pytest

from crisisops.modules.evacuation.models import Shelter, ShelterAdmission


def url_estado(refugio_id: int) -> str:
    return f"/api/v1/evacuation/shelters/{refugio_id}/status"


def url_admision(refugio_id: int) -> str:
    return f"/api/v1/evacuation/shelters/{refugio_id}/admissions"


def url_salida(refugio_id: int) -> str:
    return f"/api/v1/evacuation/shelters/{refugio_id}/departures"


def recargar(db_session, refugio: Shelter) -> Shelter:
    db_session.expire_all()
    return db_session.get(Shelter, refugio.id)


def test_cerrar_refugio_deshabilita_admisiones(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=10, ocupacion=3, estado="OPEN")

    response = client.patch(url_estado(refugio.id), json={"status": "CLOSED"})

    assert response.status_code == 200
    body = response.json()
    assert body["estado_anterior"] == "OPEN"
    assert body["estado_actual"] == "CLOSED"
    assert body["admite_ingresos"] is False

    admision = client.post(
        url_admision(refugio.id), json={"evacuee_code": "CIV-001", "people_count": 1}
    )
    assert admision.status_code == 409
    refugio = recargar(db_session, refugio)
    assert refugio.current_occupancy == 3
    assert db_session.query(ShelterAdmission).count() == 0


def test_abrir_refugio_habilita_admisiones(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=10, ocupacion=3, estado="CLOSED")

    response = client.patch(url_estado(refugio.id), json={"status": "OPEN"})

    assert response.status_code == 200
    assert response.json()["estado_actual"] == "OPEN"
    assert response.json()["admite_ingresos"] is True

    admision = client.post(
        url_admision(refugio.id), json={"evacuee_code": "CIV-001", "people_count": 2}
    )
    assert admision.status_code == 201
    assert recargar(db_session, refugio).current_occupancy == 5


def test_refugio_planned_no_admite_hasta_habilitarlo(client, crear_refugio):
    refugio = crear_refugio(capacidad=10, ocupacion=0, estado="PLANNED")
    datos = {"evacuee_code": "CIV-001", "people_count": 1}

    antes = client.post(url_admision(refugio.id), json=datos)
    client.patch(url_estado(refugio.id), json={"status": "OPEN"})
    despues = client.post(url_admision(refugio.id), json=datos)

    assert antes.status_code == 409
    assert "no admite ingresos" in antes.json()["detail"]
    assert despues.status_code == 201


def test_habilitar_refugio_sin_cupos_queda_full(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=5, ocupacion=5, estado="CLOSED")

    response = client.patch(url_estado(refugio.id), json={"status": "OPEN"})

    assert response.status_code == 200
    assert response.json()["estado_actual"] == "FULL"
    assert response.json()["admite_ingresos"] is False
    assert recargar(db_session, refugio).status == "FULL"


def test_cerrar_refugio_conserva_ocupacion_y_permite_salidas(
    client, db_session, crear_refugio, crear_admision
):
    refugio = crear_refugio(capacidad=10, ocupacion=3, estado="OPEN")
    admision = crear_admision(refugio, personas=1)

    cierre = client.patch(url_estado(refugio.id), json={"status": "CLOSED"})
    salida = client.post(url_salida(refugio.id), json={"admission_id": admision.id})

    assert cierre.json()["ocupacion_actual"] == 3
    assert salida.status_code == 200
    refugio = recargar(db_session, refugio)
    assert refugio.current_occupancy == 2
    assert refugio.status == "CLOSED"


def test_pedir_el_mismo_estado_no_cambia_nada(client, db_session, crear_refugio):
    refugio = crear_refugio(capacidad=10, ocupacion=3, estado="CLOSED")

    response = client.patch(url_estado(refugio.id), json={"status": "CLOSED"})

    assert response.status_code == 200
    assert response.json()["estado_anterior"] == "CLOSED"
    assert response.json()["estado_actual"] == "CLOSED"
    assert recargar(db_session, refugio).status == "CLOSED"


@pytest.mark.parametrize("cuerpo", [{"status": "FULL"}, {"status": "PLANNED"}, {"status": "X"}, {}])
def test_solo_se_acepta_open_o_closed(client, db_session, crear_refugio, cuerpo):
    refugio = crear_refugio(capacidad=10, ocupacion=3, estado="OPEN")

    response = client.patch(url_estado(refugio.id), json=cuerpo)

    assert response.status_code == 422
    assert recargar(db_session, refugio).status == "OPEN"


def test_refugio_inexistente_responde_404(client):
    response = client.patch(url_estado(999), json={"status": "CLOSED"})

    assert response.status_code == 404
    assert "999" in response.json()["detail"]
