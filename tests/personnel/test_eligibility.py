
from datetime import datetime
from unittest.mock import Mock

from crisisops.modules.personnel.service import PersonnelService

INICIO = datetime(2026, 11, 1, 10)
FIN = datetime(2026, 11, 1, 14)


def repo_con_brigadista_apto():
    """Un repository falso donde el brigadista 1 cumple todas las reglas."""
    repo = Mock()
    repo.get_active_responders.return_value = [Mock(id=1)]
    repo.get_covering_shift.return_value = Mock()  # tiene turno
    repo.responder_has_skill.return_value = Mock()  # tiene la skill
    repo.get_skill.return_value = Mock(requires_certification=True)
    repo.get_valid_certification.return_value = Mock()  # certificación vigente
    repo.get_overlapping_assignments.return_value = []  # sin choques
    return repo


def buscar(repo):
    return PersonnelService(repo).get_eligible_responders(["RESCATE"], INICIO, FIN)


def test_brigadista_que_cumple_todo_es_elegible():
    assert len(buscar(repo_con_brigadista_apto())) == 1


def test_brigadista_fuera_de_turno_no_es_elegible():
    repo = repo_con_brigadista_apto()
    repo.get_covering_shift.return_value = None
    assert buscar(repo) == []


def test_brigadista_sin_skill_requerida_no_es_elegible():
    repo = repo_con_brigadista_apto()
    repo.responder_has_skill.return_value = None
    assert buscar(repo) == []


def test_brigadista_con_certificacion_vencida_no_es_elegible():
    repo = repo_con_brigadista_apto()
    repo.get_valid_certification.return_value = None
    assert buscar(repo) == []


def test_brigadista_con_asignacion_solapada_no_es_elegible():
    repo = repo_con_brigadista_apto()
    repo.get_overlapping_assignments.return_value = [Mock()]
    assert buscar(repo) == []