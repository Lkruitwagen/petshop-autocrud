from enum import Enum
from typing import Any

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PORT: str | None = Field(None, env="PORT")

    # Database
    PG_DB_USER: str = Field(..., env="PG_DB_USER")
    PG_DB_PW: str = Field(..., env="PG_DB_PW")
    PG_DB_HOST: str = Field(..., env="PG_DB_HOST")
    PG_DB_PORT: str = Field(..., env="PG_DB_PORT")
    PG_DB_NAME: str = Field(..., env="PG_DB_NAME")

    SQLALCHEMY_DATABASE_URL: str | None = None
    ALEMBIC_ROOT: str = "alembic"
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 2

    @validator("SQLALCHEMY_DATABASE_URL", pre=False, always=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if values.get("PG_DB_USER") is None:
            raise ValueError(
                "PG_DB_USER must be set- check env file- have you run source env.sh?"
            )
        if isinstance(v, str):
            return v
        else:
            return str(
                PostgresDsn.build(
                    scheme="postgresql",
                    username=values.get("PG_DB_USER"),
                    password=values.get("PG_DB_PW"),
                    host=values.get("PG_DB_HOST"),
                    port=int(values.get("PG_DB_PORT")),
                    path=f'{values.get("PG_DB_NAME")}',
                )
            )

    class Config:
        case_sensitive = True


settings = Settings()
