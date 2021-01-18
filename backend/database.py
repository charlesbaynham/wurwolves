import os
from contextlib import contextmanager

from dotenv import find_dotenv
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())


engine = None
Session = None


def load():
    # an Engine, which the Session will use for connection
    # resources
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError(
            "Env var DATABASE_URL not set. If you are running for "
            "development, copy the .env.example file to .env"
        )

    global engine
    global Session

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


load()
