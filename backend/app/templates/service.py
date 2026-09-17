from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import AppError
from app.questions.enums import Direction, QuestionType
from app.templates import repository
from app.templates.models import InterviewTemplate

_TECH_SEGMENTS = [
    {"type": "self_introduction", "count": 1},
    {"type": "technical", "count": 4},
    {"type": "behavioral", "count": 2},
    {"type": "open_ended", "count": 1},
]

PRESET_TEMPLATES = [
    {"name": "前端开发面试", "direction": "technical_frontend", "segments": _TECH_SEGMENTS},
    {"name": "后端开发面试", "direction": "technical_backend", "segments": _TECH_SEGMENTS},
    {"name": "算法工程师面试", "direction": "technical_algorithm", "segments": _TECH_SEGMENTS},
    {
        "name": "产品经理面试",
        "direction": "product",
        "segments": [
            {"type": "self_introduction", "count": 1},
            {"type": "behavioral", "count": 3},
            {"type": "project_experience", "count": 2},
            {"type": "open_ended", "count": 1},
        ],
    },
    {
        "name": "运营面试",
        "direction": "operations",
        "segments": [
            {"type": "self_introduction", "count": 1},
            {"type": "behavioral", "count": 2},
            {"type": "open_ended", "count": 2},
        ],
    },
    {
        "name": "通用行为面试",
        "direction": "general",
        "segments": [
            {"type": "self_introduction", "count": 1},
            {"type": "behavioral", "count": 3},
            {"type": "open_ended", "count": 1},
        ],
    },
]


def list_templates(db: DbSession) -> list[InterviewTemplate]:
    return repository.list_all(db)


def validate_config(direction: str, segments: list[dict]) -> tuple[str, list[dict]]:
    if direction not in {item.value for item in Direction}:
        raise AppError(code=40001, message="无效的岗位方向")
    if not segments:
        raise AppError(code=40006, message="题型组合不能为空")

    normalized: list[dict] = []
    total = 0
    for segment in segments:
        if segment["type"] not in {item.value for item in QuestionType}:
            raise AppError(code=40002, message="无效的题型")
        if segment["count"] < 1:
            raise AppError(code=40007, message="每环节题目数量至少为 1")
        normalized.append({"type": segment["type"], "count": segment["count"]})
        total += segment["count"]

    if total > 20:
        raise AppError(code=40005, message="题目总数须在 1-20 之间")
    return direction, normalized


def resolve_config(
    db: DbSession,
    template_id: int | None = None,
    custom_config: tuple[str, list[dict]] | None = None,
) -> tuple[str, list[dict]]:
    if template_id is not None:
        template = repository.get_by_id(db, template_id)
        if template is None:
            raise AppError(code=40402, message="模板不存在", status_code=404)
        return template.direction, template.segments
    if custom_config is not None:
        direction, segments = custom_config
        return validate_config(direction, segments)
    raise AppError(code=40008, message="必须提供模板或自定义配置")


def seed_if_empty(db: DbSession) -> None:
    if repository.count(db) > 0:
        return
    repository.bulk_insert(
        db, [InterviewTemplate(**item) for item in PRESET_TEMPLATES]
    )
