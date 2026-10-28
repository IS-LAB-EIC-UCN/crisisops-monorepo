'''T-4.5: El registro inicial de una emergencia se envía y persiste correctamente'''

from sqlalchemy import func, select

from crisisops.modules.emergencies.enums import EmergencyStatus, EmergencyType
from crisisops.modules.emergencies.models import Emergency

URL = "/api/v1/emergencies"

VALID_REPORT = {
    "type": "FIRE",
    "reported_by": "operator1",
    "title": "Incendio_prueba",
    "description": "Estamos realizando un reporte d prueba para testing",
    "location_description": "Zona A",
}

def _count_rows(db_session) -> int:
    return db_session.scalar(select(func.count()).select_from(Emergency))

def _reload(db_session, emergency_id: int) -> Emergency | None:
    #expire_all descarta lo cacheado en la sesión: obliga a leer de la BD de verdad.
    db_session.expire_all()
    return db_session.get(Emergency, emergency_id)

def test_valid_report_is_accepted_and_echoed(client):
    response = client.post(URL, json=VALID_REPORT)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["status"] == "REPORTED"
    assert body["type"] == "FIRE"
    assert body["title"] == VALID_REPORT["title"]

def test_valid_report_is_persisted_with_all_fields(client, db_session):
    emergency_id = client.post(URL, json=VALID_REPORT).json()["id"]

    saved = _reload(db_session, emergency_id)

    assert saved is not None
    assert saved.type == EmergencyType.FIRE 
    assert saved.status == EmergencyStatus.REPORTED 
    assert saved.reported_by == "operator1"
    assert saved.title == VALID_REPORT["title"]
    assert saved.description == VALID_REPORT["description"]
    assert saved.location_description == VALID_REPORT["location_description"]
    assert saved.created_at is not None


def test_minimal_report_is_persisted_with_empty_optional_fields(client, db_session):
   
    payload = {"type": "FLOOD", "reported_by":"operator1"}

    emergency_id = client.post(URL, json=payload).json()["id"]

    saved = _reload(db_session, emergency_id)

    assert saved is not None
    assert saved.status == EmergencyStatus.REPORTED
    assert saved.title is None
    assert saved.description is None
    assert saved.location_description is None

def test_each_report_creates_its_own_row(client, db_session):
    '''se envia el mismo reporte dos veces, los ids son distintos, 
    así que cada envio crea una emergencia nueva. Deben haber exactamente 2 filas en la tabla'''
     
    first = client.post(URL, json=VALID_REPORT).json()["id"]
    second = client.post(URL, json=VALID_REPORT).json()["id"]

    assert first != second
    assert _count_rows(db_session) == 2

def test_rejected_report_is_not_persisted(client, db_session):
    response = client.post(URL, json={"type": "TORNADO", "reported_by":"operator1"})

    assert response.status_code == 422
    assert _count_rows(db_session) == 0



