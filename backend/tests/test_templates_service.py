import pytest

from app.core.exceptions import AppError
from app.templates import service

VALID_SEGMENTS = [
    {"type": "self_introduction", "count": 1},
    {"type": "technical", "count": 3},
]


def test_seed_if_empty_creates_preset_templates(db_session):
    service.seed_if_empty(db_session)
    assert len(service.list_templates(db_session)) >= 3


def test_seed_if_empty_is_idempotent(db_session):
    service.seed_if_empty(db_session)
    first = len(service.list_templates(db_session))
    service.seed_if_empty(db_session)
    assert len(service.list_templates(db_session)) == first


def test_validate_config_returns_direction_and_segments(db_session):
    direction, segments = service.validate_config("general", VALID_SEGMENTS)
    assert direction == "general"
    assert segments == VALID_SEGMENTS


def test_validate_config_rejects_invalid_direction(db_session):
    with pytest.raises(AppError):
        service.validate_config("nope", VALID_SEGMENTS)


def test_validate_config_rejects_empty_segments(db_session):
    with pytest.raises(AppError):
        service.validate_config("general", [])


def test_validate_config_rejects_invalid_type(db_session):
    with pytest.raises(AppError):
        service.validate_config("general", [{"type": "nope", "count": 1}])


def test_validate_config_rejects_zero_count(db_session):
    with pytest.raises(AppError):
        service.validate_config("general", [{"type": "technical", "count": 0}])


def test_validate_config_rejects_total_over_20(db_session):
    with pytest.raises(AppError):
        service.validate_config("general", [{"type": "technical", "count": 21}])


def test_resolve_config_by_template_id(db_session):
    service.seed_if_empty(db_session)
    template = service.list_templates(db_session)[0]
    direction, segments = service.resolve_config(db_session, template_id=template.id)
    assert direction == template.direction
    assert segments == template.segments


def test_resolve_config_missing_template_raises(db_session):
    with pytest.raises(AppError):
        service.resolve_config(db_session, template_id=99999)


def test_resolve_config_by_custom_config(db_session):
    direction, segments = service.resolve_config(
        db_session, custom_config=("general", VALID_SEGMENTS)
    )
    assert direction == "general"
    assert segments == VALID_SEGMENTS


def test_resolve_config_without_input_raises(db_session):
    with pytest.raises(AppError):
        service.resolve_config(db_session)
