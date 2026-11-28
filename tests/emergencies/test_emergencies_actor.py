"""Identificación del actor y su rol mediante cabeceras (sin inicio de sesión)."""

from sqlalchemy import select

from crisisops.modules.emergencies.models import EmergencyAuditLog

URL = "/api/v1/emergencies"

REPORT = {"type": "FIRE", "date_time": "2026-10-20T10:00:00Z", "reported_by": "operator1"}


def test_write_without_headers_is_rejected(anonymous_client, db_session):
    response = anonymous_client.post(URL, json=REPORT)

    assert response.status_code == 422
    assert db_session.scalars(select(EmergencyAuditLog)).all() == []


def test_write_without_role_header_is_rejected(anonymous_client):
    response = anonymous_client.post(URL, json=REPORT, headers={"X-Actor": "maria.perez"})

    assert response.status_code == 422


def test_write_without_actor_header_is_rejected(anonymous_client):
    response = anonymous_client.post(URL, json=REPORT, headers={"X-Actor-Role": "OPERATOR"})

    assert response.status_code == 422


def test_invalid_actor_header_is_rejected(anonymous_client, headers_for):
    for bad_value in ("ab", "con espacios", "x" * 51, "<script>"):
        response = anonymous_client.post(
            URL, json=REPORT, headers=headers_for("OPERATOR", bad_value)
        )

        assert response.status_code == 422, bad_value


def test_unknown_role_is_rejected(anonymous_client):
    response = anonymous_client.post(
        URL, json=REPORT, headers={"X-Actor": "maria.perez", "X-Actor-Role": "SUPERUSER"}
    )

    assert response.status_code == 422


def test_audit_records_the_actor_sent_in_the_headers(anonymous_client, db_session, headers_for):
    operator = headers_for("OPERATOR", "maria.perez")
    created = anonymous_client.post(URL, json=REPORT, headers=operator)
    assert created.status_code == 201, created.text

    anonymous_client.patch(
        f"{URL}/{created.json()['id']}",
        json={"title": "Incendio forestal en el cerro norte"},
        headers=headers_for("COORDINATOR", "juan_lopez"),
    )

    db_session.expire_all()
    logs = db_session.scalars(select(EmergencyAuditLog).order_by(EmergencyAuditLog.id)).all()
    assert [(log.actor, log.actor_role.value) for log in logs] == [
        ("maria.perez", "OPERATOR"),
        ("juan_lopez", "COORDINATOR"),
    ]


def test_reads_and_health_do_not_need_the_headers(anonymous_client, client):
    emergency_id = client.post(URL, json=REPORT).json()["id"]

    assert anonymous_client.get(f"{URL}/health").status_code == 200
    assert anonymous_client.get(f"{URL}/{emergency_id}/fields").status_code == 200
    assert anonymous_client.get(f"{URL}/{emergency_id}/audit").status_code == 200