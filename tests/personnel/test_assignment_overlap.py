from datetime import UTC, datetime

import pytest

from crisisops.modules.personnel.models import PersonnelAssignment


def dt(hour: int) -> datetime:
    return datetime(2026, 11, 1, hour, 0, tzinfo=UTC)


@pytest.fixture
def assignment() -> PersonnelAssignment:
    return PersonnelAssignment(responder_id=1, start_at=dt(10), end_at=dt(14))


def test_separated_intervals_do_not_overlap(assignment):
    assert assignment.overlaps(dt(15), dt(18)) is False

def test_contained_interval_overlaps(assignment):
    assert assignment.overlaps(dt(11), dt(12)) is True

def test_partial_overlap_at_start(assignment):
    assert assignment.overlaps(dt(8), dt(11)) is True

def test_partial_overlap_at_end(assignment):
    assert assignment.overlaps(dt(13), dt(16)) is True

def test_touching_boundaries_do_not_overlap(assignment):
    assert assignment.overlaps(dt(14), dt(16)) is False  # [10,14) vs [14,16)
    assert assignment.overlaps(dt(8), dt(10)) is False

def test_invalid_interval_raises(assignment):
    with pytest.raises(ValueError):
        assignment.overlaps(dt(12), dt(12))