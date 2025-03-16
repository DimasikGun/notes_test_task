from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    def get_full_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class JWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 30
    TOKEN_TYPE_FIELD: str = "type"
    ACCESS_TOKEN_TYPE: str = "access"
    REFRESH_TOKEN_TYPE: str = "refresh"


class DbConfig(BaseModel):
    url: PostgresDsn
    test_url: PostgresDsn
    test_admin_url: PostgresDsn
    test_name: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class AIConfig(BaseModel):
    api_key: str
    default_model: str = "gemini-2.0-flash"
    summarization_prompt: str = (
        "You are an AI designed to generate concise summaries of notes. "
        "Given a note's title and text, provide the shortest possible summary "
        "while preserving the key meaning. Maintain the original language of the note. "
        "Avoid unnecessary details and keep the response as brief as possible."
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    db: DbConfig
    ai: AIConfig
    jwt: JWT = JWT()
    run: RunConfig = RunConfig()


settings = Settings()
