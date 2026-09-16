import os


class Settings:
    def __init__(self) -> None:
        self.database_url = os.environ.get("DATABASE_URL", "sqlite:///./interview.db")
        self.seed_questions_path = os.environ.get(
            "SEED_QUESTIONS_PATH", "backend/app/questions/seed_data.json"
        )
        self.request_body_limit = int(
            os.environ.get("REQUEST_BODY_LIMIT", str(1024 * 1024))
        )


settings = Settings()
