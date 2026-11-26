# Tests por función · operations

| Función | Archivo | Test |
|---|---|---|
| `OperationsService.validate_emergency` | `service/operation.py` | `test_active_emergency_allows_continuation`<br>`test_invalid_emergency_raises_domain_error`<br>`test_unavailable_emergency_service_raises_503` |
| `OperationsService.create_operation` | `service/operation.py` | `test_create_operation_with_active_emergency_returns_201`<br>`test_failed_commit_rolls_back_and_propagates_error` |
| `OperationsService.get_operation` | `service/operation.py` | `test_get_existing_operation_returns_200`<br>`test_get_missing_operation_returns_404` |
| `MissionsService.create_mission` | `service/mission.py` | `test_create_mission_returns_201_and_planned`<br>`test_create_mission_for_missing_operation_returns_404_without_saving` |
| `MissionsService.get_mission` | `service/mission.py` | `test_get_mission_returns_200_with_resource_and_personnel_requirements`<br>`test_get_missing_mission_returns_404` |
| `MissionsService.add_requirement` | `service/mission.py` | `test_add_valid_requirement_returns_201`<br>`test_add_unknown_catalog_value_returns_422_without_saving`<br>`test_add_resource_requirement_when_group_b_is_down_returns_503_without_saving`<br>`test_add_personnel_requirement_when_group_c_is_down_returns_503_without_saving` |
| `create_operation` | `router/operations.py` | `test_create_operation_with_active_emergency_returns_201`<br>`test_create_operation_with_missing_emergency_returns_422`<br>`test_create_operation_with_inactive_emergency_returns_409`<br>`test_create_operation_when_group_a_is_down_returns_503`<br>`test_group_a_not_integrated_yet_returns_503` |
| `get_operation_by_id` | `router/operations.py` | `test_get_existing_operation_returns_200`<br>`test_get_missing_operation_returns_404` |
| `create_mission` | `router/missions.py` | `test_create_mission_returns_201_and_planned`<br>`test_create_mission_for_missing_operation_returns_404_without_saving` |
| `add_mission_requirement` | `router/missions.py` | `test_add_valid_requirement_returns_201`<br>`test_add_unknown_catalog_value_returns_422_without_saving` |
| `get_mission_by_id` | `router/missions.py` | `test_get_mission_returns_200_with_resource_and_personnel_requirements`<br>`test_get_missing_mission_returns_404` |
