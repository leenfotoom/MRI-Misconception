from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL


def _print_database_url_debug(database_url: str) -> None:
    url = make_url(database_url)
    print(
        "[database] DATABASE_URL loaded: "
        f"driver={url.drivername} "
        f"user={url.username or ''} "
        f"host={url.host or ''} "
        f"port={url.port or ''} "
        f"database={url.database or ''}"
    )


_print_database_url_debug(DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
