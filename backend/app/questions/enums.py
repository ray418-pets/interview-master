import enum


class Direction(str, enum.Enum):
    TECHNICAL_FRONTEND = "technical_frontend"
    TECHNICAL_BACKEND = "technical_backend"
    TECHNICAL_ALGORITHM = "technical_algorithm"
    PRODUCT = "product"
    OPERATIONS = "operations"
    GENERAL = "general"


class QuestionType(str, enum.Enum):
    SELF_INTRODUCTION = "self_introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PROJECT_EXPERIENCE = "project_experience"
    OPEN_ENDED = "open_ended"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
