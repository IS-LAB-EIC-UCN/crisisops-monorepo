'''T-4.5: El registro inicial de una emergencia se envía y persiste correctamente'''

from sqlalchemy import func, select
from crisisops.modules.emergencies.enums import EmergencyStatus, EmergencyType
from crisisops.modules.emergencies.models import Emergency
from copy import deepcopy
import pytest
from httpx import Response

URL_CREATION = "/api/v1/emergencies"
URL_VALIDATIONS_FIELDS = "/api/v1/emergencies/{emergency_id}/fields"

VALID_REPORT = {
    "type":"FIRE",
    "reported_by": "operator1",
    "title": "Incendio de prueba",
    "description":("Estamos realizando un reporte de prueba para testing"
                   "dedjedjededededededededededededededededededed"
                   "ddiadjiuadeufiesufhieuhfuisehfuiehfiusehfuiehfiuehfuieshf"
                   "kanowadijwoaidjoawjdowjadowiadjowajdowajdowjodleidjejdiejd"
                   ),
    "location_description":"Zona A, La Serena",
    "severity":"HIGH",
}

def _create_emergency(client, report: dict) -> int: 
    response = client.post(URL_CREATION, json=report) #se enviar el reporte para su creación utilizando URL_CREATION como ruta en donde se encuentra la función 
    assert  response.status_code == 201, response.text #se comprueba que el status de crespuesta de la creación sea el correcto 201
    body = response.json() #se obtiene el cuerpo de la respuesta de la creación
    assert "id" in body, body #se verifica que el cuerpo tenga una campo llamado "id"
    return body["id"] #se retorna el id

def _validate_fields(client, emergency_id: int) -> Response:
    return client.get(URL_VALIDATIONS_FIELDS.format(emergency_id = emergency_id))


def _reload(db_session, emergency_id: int) -> Emergency | None:
    #expire_all descarta lo cacheado en la sesión: obliga a leer de la BD de verdad.
    db_session.expire_all()
    return db_session.get(Emergency, emergency_id)

def test_valid_report_fields(client, db_session):
    emergency_id = _create_emergency(client, VALID_REPORT)

    response = _validate_fields(client, emergency_id)

    assert response.status_code == 200, response.text
    body = response.json()

    print("\nRESPUESTA DE ENDPOINT")
    print(body)
    
    assert body["emergency_id"] == emergency_id
    assert body["ready_for_validation"] is True
    assert body["errors_fields"] == {}

    emergency = _reload(db_session, emergency_id)

    assert emergency is not None
    assert emergency.status == EmergencyStatus.REPORTED

def test_incomplete_report_fields(client, db_session):
    report = VALID_REPORT.copy()

    report.pop("description")
    report.pop("severity")

    emergency_id = _create_emergency(client, report)

    response = _validate_fields(client, emergency_id)

    assert response.status_code == 200, response.text

    body = response.json()

    assert body["emergency_id"] == emergency_id
    assert body["ready_for_validation"] is False

    assert "description" in body["errors_fields"]
    assert "severity" in body["errors_fields"]

    emergency = _reload(db_session, emergency_id)

    assert emergency is not None
    assert emergency.status == EmergencyStatus.REPORTED

    


