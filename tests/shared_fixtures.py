import logging
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

TESTING_DB_URL = "sqlite:///testing.db"
NPM_ROOT_DIR = Path(__file__, "../../").resolve()


@contextmanager
def cd(directory):
    owd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(owd)


@pytest.fixture(scope="session")
def test_server():
    """
    Launch and finally close a test server
    """

    import subprocess as sp

    with cd(NPM_ROOT_DIR):
        logging.info("Building site...")

        sp.run(["npm", "run", "build"], stdout=sp.PIPE)

        logging.info("Launching server...")

        dev_process = sp.Popen(
            ["npm", "run", "start"],
            stdout=sp.PIPE,
        )

    yield None

    dev_process.terminate()


@pytest.fixture()
def clean_server(test_server):
    """
    Launch a server if needed, and clean the database
    """
    import backend.database
    from backend.model import Base

    backend.database.load()
    engine = backend.database.engine

    Base.metadata.bind = engine

    Base.metadata.drop_all()
    Base.metadata.create_all()

    return test_server


@pytest.fixture(scope="session")
def engine():
    """Return an engine to the database.

    This fixture should not be used as the database is not cleaned between
    invocations. Use db_session instead.
    """
    os.environ["DATABASE_URL"] = TESTING_DB_URL

    import backend.database

    backend.database.load()

    return backend.database.engine


@pytest.fixture
def db_session(engine):
    """
    Get an SQLAlchemy database session to a clean database with the model schema
    set up.
    """
    from backend.model import Base
    from backend.database import Session

    Base.metadata.bind = engine

    Base.metadata.drop_all()
    Base.metadata.create_all()

    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(db_session):
    """
    Get a FastAPI TestClient pointing at the app with a clean database session
    """
    from fastapi.testclient import TestClient
    from backend.main import app

    return TestClient(app)
