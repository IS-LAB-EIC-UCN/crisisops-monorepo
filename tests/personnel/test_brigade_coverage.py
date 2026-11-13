from unittest.mock import Mock

from crisisops.modules.personnel.service import PersonnelService


def repo_con_habilidades(asignaciones: dict[int, list[str]]):

    repo = Mock()

    def responder_has_skill(responder_id: int, skill_code: str):
        skills_del_brigadista = asignaciones.get(responder_id, [])
        if skill_code in skills_del_brigadista:
            return Mock(responder_id=responder_id, skill_code=skill_code)
        return None

    repo.responder_has_skill.side_effect = responder_has_skill
    return repo


def test_cobertura_completa_un_solo_brigadista():
    
    repo = repo_con_habilidades({1: ["PARAMEDIC", "DRIVER"]})
    service = PersonnelService(repo)

    faltantes = service.validate_brigade_coverage([1], ["PARAMEDIC", "DRIVER"])
    assert faltantes == []


def test_cobertura_completa_distribuida_en_la_brigada():
   
    repo = repo_con_habilidades({
        1: ["PARAMEDIC"],
        2: ["DRIVER"],
        3: ["RESCUE"],
    })
    service = PersonnelService(repo)

    faltantes = service.validate_brigade_coverage([1, 2, 3], ["PARAMEDIC", "DRIVER", "RESCUE"])
    assert faltantes == []


def test_competencia_faltante_identificada():

    repo = repo_con_habilidades({
        1: ["PARAMEDIC"],
        2: ["DRIVER"],
    })
    service = PersonnelService(repo)

    faltantes = service.validate_brigade_coverage([1, 2], ["PARAMEDIC", "DRIVER", "RESCUE"])
    assert faltantes == ["RESCUE"]


def test_multiples_competencias_faltantes():
    
    repo = repo_con_habilidades({1: ["PARAMEDIC"]})
    service = PersonnelService(repo)

    faltantes = service.validate_brigade_coverage([1], ["PARAMEDIC", "DRIVER", "RESCUE", "HAZMAT"])
    assert sorted(faltantes) == ["DRIVER", "HAZMAT", "RESCUE"]


def test_ninguna_competencia_cubierta():

    repo = repo_con_habilidades({1: ["OTHER"], 2: ["NONE"]})
    service = PersonnelService(repo)

    faltantes = service.validate_brigade_coverage([1, 2], ["PARAMEDIC", "DRIVER"])
    assert sorted(faltantes) == ["DRIVER", "PARAMEDIC"]
