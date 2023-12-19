from typing import Any

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import JSON

from .config import settings


def generate_engine() -> sqlalchemy.engine.base.Engine:

    return create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
    )


engine = generate_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}


# Dependency
def get_db() -> Session:
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()
