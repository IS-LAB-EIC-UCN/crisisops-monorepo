from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from crisisops.modules.personnel.models import Certification
from crisisops.modules.personnel.schemas import CertificationCreate


def dt(hour: int, day: int = 1) -> datetime:
    return datetime(2026, 11, day, hour, 0, tzinfo=UTC)


@pytest.fixture
def cert() -> Certification:
    return Certification(
        responder_id=1,
        skill_code="PARAMEDIC",
        issued_at=dt(0, day=1),
        expires_at=dt(0, day=10),
    )


def test_certificacion_vigente_cubre_todo_el_intervalo(cert):
    assert cert.is_valid_for(dt(0, day=2), dt(0, day=5)) is True


def test_certificacion_que_vence_en_medio_del_intervalo_retorna_false(cert):
    assert cert.is_valid_for(dt(0, day=5), dt(0, day=12)) is False


def test_certificacion_emitida_despues_del_inicio_retorna_false(cert):
    cert_tardia = Certification(
        responder_id=1,
        skill_code="PARAMEDIC",
        issued_at=dt(0, day=3),
        expires_at=dt(0, day=10),
    )
    assert cert_tardia.is_valid_for(dt(0, day=1), dt(0, day=5)) is False


def test_certificacion_ya_expirada_retorna_false(cert):
    assert cert.is_valid_for(dt(0, day=15), dt(0, day=20)) is False


def test_esquema_rechaza_expires_at_anterior_o_igual_a_issued_at():
    with pytest.raises(ValidationError):
        CertificationCreate(
            skill_code="PARAMEDIC",
            issued_at=dt(10),
            expires_at=dt(10),
        )

    with pytest.raises(ValidationError):
        CertificationCreate(
            skill_code="PARAMEDIC",
            issued_at=dt(15),
            expires_at=dt(10),
        )
