from datetime import date

from sqlalchemy import select

from crisisops.modules.resources.models import Resource, implementos

URL = "/api/v1/resources"

FICHA = {
    "nombreRecurso": "Extintor de incendio 6 kg",
    "estadoRecurso": "DISPONIBLE",
    "peso": 9.5,
    "tipoRecurso": "IMPLEMENTO",
    "tipoImplemento": "Extintor de incendio",
    "tipoUso": "Seguridad",
    "estadoFisico": "BUENO",
}

def test_registro_valido(client, db_session):
    # Responde 201 y queda guardado

    response = client.post(URL, json=FICHA)

    assert response.status_code == 201
    body = response.json()
    assert body["idRecurso"] is not None
    assert body["estadoRecurso"] == "DISPONIBLE"
    assert body["tipoRecurso"] == "IMPLEMENTO"
    assert body["fechaIngreso"] == date.today().isoformat()
    assert body["anio"] == date.today().year
    db_session.expire_all()
    recurso = db_session.get(Resource, body["idRecurso"])
    implemento = db_session.get(implementos, body["idRecurso"])
    assert recurso is not None
    assert recurso.estado_recurso == "DISPONIBLE"
    assert implemento is not None
    assert implemento.tipo_uso == "Seguridad"

def test_ficha_incompleta(client, db_session):
    # Responde 422 y no guarda

    ficha_incompleta = {k: v for k, v in FICHA.items() if k != "tipoUso"}

    response = client.post(URL, json=ficha_incompleta)

    assert response.status_code == 422
    assert db_session.scalars(select(Resource)).all() == []

def test_en_mantenimiento_no_aparece(client):
    # Responde 200 y solo muestra los recursos DISPONIBLE

    disponible = client.post(URL, json=FICHA).json()
    client.post(
        URL, json={**FICHA, "nombreRecurso": "Hacha", "estadoRecurso": "EN MANTENIMIENTO"}
    )

    response = client.get(f"{URL}/disponibles")

    assert response.status_code == 200
    ids = [recurso["idRecurso"] for recurso in response.json()]
    assert ids == [disponible["idRecurso"]]