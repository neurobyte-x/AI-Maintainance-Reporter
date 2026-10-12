from backend.db.base import Base
from backend.db.session import get_engine
from backend.models import ticket, user


def init_db() -> None:
    try:
        engine = get_engine()
    except RuntimeError as exc:
        print(f"WARNING: {str(exc)}")
        return

    Base.metadata.create_all(bind=engine)
