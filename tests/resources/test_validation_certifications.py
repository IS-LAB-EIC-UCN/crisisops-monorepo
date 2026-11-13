from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from crisisops.modules.personnel.models import Certification, Responder, ResponderSkill, Skill
from crisisops.modules.resources.models import Resource, implementos

URL = "/api/v1/resources"

def _cargar_operadores_prueba(db_session):
    ahora = datetime.now(timezone.utc)

    db_session.add_all([
        Skill(code="OP_GRUA", name="Operación de Grúa", requires_certification=True),
        Skill(code="OP_DRON", name="Piloto de Dron", requires_certification=True),
        Responder(id=1, name="Carlos Ruiz", badge_number="B-001", role="OPERADOR", is_active=True),
        Responder(id=2, name="Ana Soto", badge_number="B-002", role="OPERADOR", is_active=True),
        Responder(id=3, name="Luis Díaz", badge_number="B-003", role="OPERADOR", is_active=True),
        Responder(id=4, name="Pedro Mora", badge_number="B-004", role="OPERADOR", is_active=False),
    ])
    db_session.flush()

    db_session.add_all([
        ResponderSkill(responder_id=1, skill_code="OP_GRUA"),
        ResponderSkill(responder_id=2, skill_code="OP_GRUA"),
        ResponderSkill(responder_id=3, skill_code="OP_GRUA"),
        ResponderSkill(responder_id=4, skill_code="OP_GRUA"),
        Certification(
            responder_id=1,
            skill_code="OP_GRUA",
            issued_at=ahora - timedelta(days=30),
            expires_at=ahora + timedelta(days=335),
        ),
        Certification(
            responder_id=3,
            skill_code="OP_GRUA",
            issued_at=ahora - timedelta(days=400),
            expires_at=ahora - timedelta(days=35),
        ),
        Certification(
            responder_id=4,
            skill_code="OP_GRUA",
            issued_at=ahora - timedelta(days=10),
            expires_at=ahora + timedelta(days=100),
        ),
    ])
    db_session.commit()


def test_operador_con_certificacion_valida(client, db_session):
    # Responde 200 cuando el operador está activo, tiene la habilidad y certificación vigente
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 1, "skill_code": "OP_GRUA"})

    assert response.status_code == 200
    body = response.json()
    assert body["valido"] is True
    assert body["responder_id"] == 1
    assert body["skill_code"] == "OP_GRUA"


def test_operador_sin_certificacion(client, db_session):
    # Responde 400 cuando el operador tiene la habilidad pero no tiene certificación
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 2, "skill_code": "OP_GRUA"})

    assert response.status_code == 400
    assert "no cuenta con certificación" in response.json()["detail"]


def test_certificacion_vencida(client, db_session):
    # Responde 400 cuando la certificación ya expiró
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 3, "skill_code": "OP_GRUA"})

    assert response.status_code == 400
    assert "vencida" in response.json()["detail"]


def test_operador_inexistente(client, db_session):
    # Responde 400 cuando el operador no existe en la base de datos
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 999, "skill_code": "OP_GRUA"})

    assert response.status_code == 400
    assert "no existe" in response.json()["detail"]


def test_operador_inactivo(client, db_session):
    # Responde 400 cuando el operador está inactivo (is_active=False)
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 4, "skill_code": "OP_GRUA"})

    assert response.status_code == 400
    assert "inactivo" in response.json()["detail"]


def test_habilidad_incorrecta(client, db_session):
    # Responde 400 cuando el operador no posee la habilidad solicitada
    _cargar_operadores_prueba(db_session)

    response = client.post(f"{URL}/validacion", json={"responder_id": 1, "skill_code": "OP_DRON"})

    assert response.status_code == 400
    assert "no posee la habilidad" in response.json()["detail"]
