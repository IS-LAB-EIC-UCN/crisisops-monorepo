"""Historia 3: registrar la salida de una persona o grupo para liberar cupos."""

from crisisops.modules.evacuation.models import Shelter, ShelterAdmission


def url(refugio_id: int) -> str:
    return f"/api/v1/evacuation/shelters/{refugio_id}/departures"


def recargar(db_session, refugio: Shelter, admision: ShelterAdmission | None = None):
    db_session.expire_all()
    r = db_session.get(Shelter, refugio.id)
    a = db_session.get(ShelterAdmission, admision.id) if admision else None
    return r, a


def test_salida_de_una_persona_libera_un_cupo(client, db_session, crear_refugio, crear_admision):
    refugio = crear_refugio(capacidad=10, ocupacion=3)
    admision = crear_admision(refugio, personas=1)

    response = client.post(url(refugio.id), json={"admission_id": admision.id})

    assert response.status_code == 200
    body = response.json()
    assert body["cupos_liberados"] == 1
    assert body["ocupacion_actual"] == 2
    assert body["cupos_disponibles"] == 8
    refugio, admision = recargar(db_session, refugio, admision)
    assert refugio.current_occupancy == 2
    assert admision.status == "DEPARTED"
    assert admision.departed_at is not None


def test_salida_de_un_grupo_libera_todos_sus_cupos(
    client, db_session, crear_refugio, crear_admision
):
    refugio = crear_refugio(capacidad=20, ocupacion=12)
    grupo = crear_admision(refugio, personas=4, codigo="GRUPO-FAM-07")

    response = client.post(url(refugio.id), json={"admission_id": grupo.id})

    assert response.status_code == 200
    assert response.json()["cupos_liberados"] == 4
    refugio, _ = recargar(db_session, refugio)
    assert refugio.current_occupancy == 8


def test_refugio_full_vuelve_a_open_al_liberar_cupos(
    client, db_session, crear_refugio, crear_admision
):
    refugio = crear_refugio(capacidad=5, ocupacion=5, estado="FULL")
    admision = crear_admision(refugio, personas=2)

    response = client.post(url(refugio.id), json={"admission_id": admision.id})

    assert response.status_code == 200
    assert response.json()["estado_refugio"] == "OPEN"
    refugio, _ = recargar(db_session, refugio)
    assert refugio.status == "OPEN"
    assert refugio.current_occupancy == 3


def test_refugio_closed_permite_salidas_y_sigue_closed(
    client, db_session, crear_refugio, crear_admision
):
    refugio = crear_refugio(capacidad=5, ocupacion=2, estado="CLOSED")
    admision = crear_admision(refugio, personas=1)

    response = client.post(url(refugio.id), json={"admission_id": admision.id})

    assert response.status_code == 200
    assert response.json()["estado_refugio"] == "CLOSED"


def test_no_se_puede_registrar_dos_veces_la_misma_salida(
    client, db_session, crear_refugio, crear_admision
):
    refugio = crear_refugio(capacidad=10, ocupacion=3)
    admision = crear_admision(refugio, personas=1)

    primera = client.post(url(refugio.id), json={"admission_id": admision.id})
    segunda = client.post(url(refugio.id), json={"admission_id": admision.id})

    assert primera.status_code == 200
    assert segunda.status_code == 409
    refugio, _ = recargar(db_session, refugio)
    assert refugio.current_occupancy == 2


def test_refugio_inexistente_responde_404(client):
    response = client.post(url(999), json={"admission_id": 1})

    assert response.status_code == 404
    assert "999" in response.json()["detail"]


def test_admision_inexistente_responde_404(client, crear_refugio):
    refugio = crear_refugio(capacidad=10, ocupacion=3)

    response = client.post(url(refugio.id), json={"admission_id": 12345})

    assert response.status_code == 404


def test_admision_de_otro_refugio_no_libera_cupos(
    client, db_session, crear_refugio, crear_admision
):
    refugio_a = crear_refugio(capacidad=10, ocupacion=3)
    refugio_b = crear_refugio(capacidad=10, ocupacion=4)
    admision_de_b = crear_admision(refugio_b, personas=1)

    response = client.post(url(refugio_a.id), json={"admission_id": admision_de_b.id})

    assert response.status_code == 404
    refugio_a, _ = recargar(db_session, refugio_a)
    refugio_b, _ = recargar(db_session, refugio_b)
    assert refugio_a.current_occupancy == 3
    assert refugio_b.current_occupancy == 4


def test_ocupacion_nunca_queda_negativa(client, db_session, crear_refugio, crear_admision):
    refugio = crear_refugio(capacidad=10, ocupacion=1)
    admision = crear_admision(refugio, personas=3)

    response = client.post(url(refugio.id), json={"admission_id": admision.id})

    assert response.status_code == 409
    refugio, admision = recargar(db_session, refugio, admision)
    assert refugio.current_occupancy == 1
    assert admision.status == "ACTIVE"


def test_admission_id_es_obligatorio_y_positivo(client, crear_refugio):
    refugio = crear_refugio()

    sin_id = client.post(url(refugio.id), json={})
    id_cero = client.post(url(refugio.id), json={"admission_id": 0})

    assert sin_id.status_code == 422
    assert id_cero.status_code == 422
