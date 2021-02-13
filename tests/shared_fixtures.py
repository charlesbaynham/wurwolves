import logging
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

TESTING_DB_URL = "sqlite:///testing.db"
TEST_API_URL = "http://localhost:8000/api/hello"
TEST_FRONTEND_URL = "http://localhost:3000/"
NPM_ROOT_DIR = Path(__file__, "../../").resolve()
STARTUP_TIMEOUT = 10

LOG_FILE = "test_server_backend.log"


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
    import os
    import signal

    with cd(NPM_ROOT_DIR):
        logging.info("Launching backend...")

        f = open(LOG_FILE, "w")
        dev_process = sp.Popen(
            ["npm", "run", "backend"],
            stdout=f,
            stderr=sp.STDOUT,
            preexec_fn=os.setsid,
        )

        wait_until_server_up(TEST_API_URL, STARTUP_TIMEOUT)

    try:
        yield dev_process
    finally:
        try:
            os.killpg(os.getpgid(dev_process.pid), signal.SIGTERM)

            try:
                dev_process.wait(timeout=3)
            except TimeoutError:
                os.killpg(os.getpgid(dev_process.pid), signal.SIGKILL)

            f.close()

            print("Server logs:")
            [print(l.strip()) for l in open(LOG_FILE, "r").readlines()]

        except ProcessLookupError:
            pass


@pytest.fixture(scope="session")
def full_server(backend_server):
    """
    Launch and finally close a test server for the backend and frontend
    """

    import subprocess as sp
    import os
    import signal

    with cd(NPM_ROOT_DIR):
        logging.info("Building site...")

        sp.run(["npm", "run", "build"], stdout=sp.PIPE)

        logging.info("Launching frontend server...")

        dev_process = sp.Popen(
            ["npm", "run", "frontend"],
            stdout=sp.PIPE,
            stderr=sp.STDOUT,
            preexec_fn=os.setsid,
        )

        wait_until_server_up(TEST_FRONTEND_URL, STARTUP_TIMEOUT)

    try:
        yield dev_process
    finally:
        os.killpg(os.getpgid(dev_process.pid), signal.SIGTERM)

        try:
            dev_process.wait(timeout=3)
        except TimeoutError:
            os.killpg(os.getpgid(dev_process.pid), signal.SIGKILL)
            dev_process.wait(timeout=3)


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
        except (ConnectionError, requests.exceptions.RequestException):
            pass

    raise TimeoutError(f"Server did not start in {timeout} seconds")


@pytest.fixture()
def clean_server(full_server):
    """
    Launch a full server if needed, and clean the database
    """
    import backend.database
    from backend.model import Base

    backend.database.load()
    engine = backend.database.engine

    Base.metadata.bind = engine

    Base.metadata.drop_all()
    Base.metadata.create_all()

    return full_server


@pytest.fixture(scope="session")
def engine():
    """Return an engine to the database.

    This fixture should not be used as the database is not cleaned between
    invocations. Use db_session instead.
    """
    if "IGNORE_TESTING_DB" not in os.environ:
        os.environ["DATABASE_URL"] = TESTING_DB_URL

    import backend.database

    backend.database.load()

    return backend.database.engine


@pytest.fixture
def db_session(engine):
    """
    Get an SQLAlchemy database session to a clean database with the model schema
    set up and seed the random number generator.
    """
    from backend.model import Base
    from backend.database import Session
    import random

    random.seed(123)

    Base.metadata.bind = engine

    Base.metadata.drop_all()
    Base.metadata.create_all()

    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(api_client_factory):
    """
    Get a FastAPI TestClient pointing at the app with a clean database session
    """
    return api_client_factory()


@pytest.fixture
def api_client_factory(db_session):
    """
    Get a factory for FastAPI TestClients pointing at the app with a clean database session
    """
    from fastapi.testclient import TestClient
    from backend.main import app

    return lambda: TestClient(app)
