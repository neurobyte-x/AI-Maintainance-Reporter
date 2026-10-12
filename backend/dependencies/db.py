from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.db.session import get_session_local


def get_db() -> Generator[Session, None, None]:
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()
