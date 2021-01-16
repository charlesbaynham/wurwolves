import logging
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

TESTING_DB_URL = "sqlite:///testing.db"
TEST_API_URL = "http://localhost:8000/api/hello"
TEST_FRONTEND_URL = "http://localhost:3000/"
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
def backend_server():
    """
    Launch and finally close a test server, just for the backend
    """

    import subprocess as sp

    with cd(NPM_ROOT_DIR):
        logging.info("Launching backend...")

        dev_process = sp.Popen(
            ["npm", "run", "backend"],
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
        )

        wait_until_server_up(TEST_API_URL, 5)

    yield dev_process

    dev_process.terminate()

    print(dev_process.stdout)


@pytest.fixture(scope="session")
def test_server(backend_server):
    """
    Launch and finally close a test server for the backend and frontend
    """

    import subprocess as sp

    with cd(NPM_ROOT_DIR):
        logging.info("Building site...")

        sp.run(["npm", "run", "build"], stdout=sp.PIPE)

        logging.info("Launching frontend server...")

        dev_process = sp.Popen(
            ["npm", "run", "frontend"],
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
        )

        wait_until_server_up(TEST_FRONTEND_URL, 5)

    yield dev_process

    dev_process.terminate()

    print(dev_process.stdout)


def wait_until_server_up(test_url, timeout):
    import requests
    import time

    interval = 0.5
    max_tries = int(timeout / interval)

    for i in range(0, max_tries):
        time.sleep(interval)

        logging.info("Connection attempt %s", i)
        try:
            r = requests.get(test_url)
            if r.ok:
                logging.info("Server up and running")
                return
        except ConnectionError:
            pass

    raise TimeoutError(f"Server did not start in {timeout} seconds")


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
