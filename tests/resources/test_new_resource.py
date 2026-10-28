from datetime import date

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

def test_registro_valido_responde_201_y_queda_guardado(client, db_session):
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