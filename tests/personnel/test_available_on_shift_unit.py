"""T4.3 - Pruebas unitarias de exclusión de personal fuera de turno o no disponible (H04)."""
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from crisisops.core.database import Base
from crisisops.modules.personnel.models import (
    AssignmentStatus,
    PersonnelAssignment,
    Responder,
    Shift,
)
from crisisops.modules.personnel.repository import PersonnelRepository
from crisisops.modules.personnel.service import PersonnelService

TABLAS = [Responder.__table__, Shift.__table__, PersonnelAssignment.__table__]
MOMENTO = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=TABLAS)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def repo(db):
    return PersonnelRepository(db)


def crear_brigadista(db, responder_id, *, is_active=True, turnos=(), asignaciones=()):
    """Crea un brigadista con sus turnos [(inicio, fin)] y asignaciones [(inicio, fin, estado)]."""
    db.add(
        Responder(
            id=responder_id,
            name=f"Brigadista {responder_id}",
            badge_number=f"B-{responder_id}",
            role="RESCUE",
            is_active=is_active,
        )
    )
    for inicio, fin in turnos:
        db.add(Shift(responder_id=responder_id, start_time=inicio, end_time=fin))
    for inicio, fin, estado in asignaciones:
        db.add(
            PersonnelAssignment(
                responder_id=responder_id, start_at=inicio, end_at=fin, status=estado
            )
        )
    db.commit()


def hora(h):
    return datetime(2026, 11, 1, h, 0, tzinfo=UTC)


TURNO_VIGENTE = (hora(8), hora(16))


def ids_disponibles(repo, momento=MOMENTO):
    return sorted(r.id for r in repo.get_available_on_shift_responders(momento))


# ---------- Repository: criterio 1 (turno activo Y disponible a la vez) ----------


def test_incluye_brigadista_disponible_y_en_turno(db, repo):
    crear_brigadista(db, 1, turnos=[TURNO_VIGENTE])

    assert ids_disponibles(repo) == [1]


def test_excluye_brigadista_no_disponible_aunque_este_en_turno(db, repo):
    crear_brigadista(db, 1, is_active=False, turnos=[TURNO_VIGENTE])

    assert ids_disponibles(repo) == []


def test_excluye_brigadista_disponible_sin_turnos(db, repo):
    crear_brigadista(db, 1)

    assert ids_disponibles(repo) == []


def test_excluye_brigadista_con_turno_futuro(db, repo):
    crear_brigadista(db, 1, turnos=[(hora(18), hora(22))])

    assert ids_disponibles(repo) == []


def test_excluye_brigadista_con_turno_ya_terminado(db, repo):
    crear_brigadista(db, 1, turnos=[(hora(0), hora(6))])

    assert ids_disponibles(repo) == []


def test_turno_que_comienza_justo_en_el_momento_se_considera_vigente(db, repo):
    crear_brigadista(db, 1, turnos=[(MOMENTO, hora(16))])

    assert ids_disponibles(repo) == [1]


def test_turno_que_termina_justo_en_el_momento_ya_no_es_vigente(db, repo):
    crear_brigadista(db, 1, turnos=[(hora(6), MOMENTO)])

    assert ids_disponibles(repo) == []


def test_varios_turnos_con_uno_vigente_no_duplica_al_brigadista(db, repo):
    crear_brigadista(db, 1, turnos=[(hora(0), hora(6)), TURNO_VIGENTE, (hora(9), hora(11))])

    assert ids_disponibles(repo) == [1]


def test_conjunto_mixto_retorna_solo_quienes_cumplen_ambos_criterios(db, repo):
    crear_brigadista(db, 1, turnos=[TURNO_VIGENTE])  # apto
    crear_brigadista(db, 2, is_active=False, turnos=[TURNO_VIGENTE])  # no disponible
    crear_brigadista(db, 3, turnos=[(hora(18), hora(22))])  # fuera de turno
    crear_brigadista(db, 4, is_active=False)  # ninguno de los dos
    crear_brigadista(db, 5, turnos=[TURNO_VIGENTE])  # apto

    assert ids_disponibles(repo) == [1, 5]


# ---------- Repository: asignaciones vigentes ----------


@pytest.mark.parametrize("estado", [AssignmentStatus.ACTIVE, AssignmentStatus.RESERVED])
def test_excluye_brigadista_con_asignacion_vigente(db, repo, estado):
    crear_brigadista(
        db, 1, turnos=[TURNO_VIGENTE], asignaciones=[(hora(9), hora(12), estado)]
    )

    assert ids_disponibles(repo) == []


@pytest.mark.parametrize(
    "estado", [AssignmentStatus.COMPLETED, AssignmentStatus.CANCELLED]
)
def test_asignacion_cerrada_no_excluye_al_brigadista(db, repo, estado):
    crear_brigadista(
        db, 1, turnos=[TURNO_VIGENTE], asignaciones=[(hora(9), hora(12), estado)]
    )

    assert ids_disponibles(repo) == [1]


def test_asignacion_fuera_del_momento_no_excluye_al_brigadista(db, repo):
    crear_brigadista(
        db,
        1,
        turnos=[TURNO_VIGENTE],
        asignaciones=[(hora(12), hora(14), AssignmentStatus.ACTIVE)],
    )

    assert ids_disponibles(repo) == [1]


# ---------- Repository: criterio 2 (cambio a no disponible) ----------


def test_cambio_a_no_disponible_lo_excluye_en_la_siguiente_consulta(db, repo):
    crear_brigadista(db, 1, turnos=[TURNO_VIGENTE])
    crear_brigadista(db, 2, turnos=[TURNO_VIGENTE])
    assert ids_disponibles(repo) == [1, 2]

    db.get(Responder, 1).is_active = False
    db.commit()

    assert ids_disponibles(repo) == [2]


def test_volver_a_disponible_lo_incluye_nuevamente(db, repo):
    crear_brigadista(db, 1, is_active=False, turnos=[TURNO_VIGENTE])
    assert ids_disponibles(repo) == []

    db.get(Responder, 1).is_active = True
    db.commit()

    assert ids_disponibles(repo) == [1]


# ---------- Service ----------


def test_service_consulta_el_repository_con_el_momento_indicado():
    repo = Mock()
    repo.get_available_on_shift_responders.return_value = ["brigadista"]
    service = PersonnelService(repo)

    resultado = service.filter_available_on_shift(moment=MOMENTO)

    repo.get_available_on_shift_responders.assert_called_once_with(MOMENTO)
    assert resultado == ["brigadista"]


def test_service_sin_momento_usa_la_hora_actual_utc():
    repo = Mock()
    repo.get_available_on_shift_responders.return_value = []
    service = PersonnelService(repo)

    antes = datetime.now(UTC)
    service.filter_available_on_shift()
    despues = datetime.now(UTC)

    (momento_usado,) = repo.get_available_on_shift_responders.call_args.args
    assert momento_usado.tzinfo is not None
    assert antes - timedelta(seconds=1) <= momento_usado <= despues
