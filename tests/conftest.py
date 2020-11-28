import logging
import os

import pytest

logging.basicConfig(level=logging.DEBUG)

TESTING_DB_URL = "sqlite:///testing.db"


def pytest_addoption(parser):
    parser.addoption(
        "--runselenium", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "selenium: marks tests as requiring selenium (select with '-m selenium')",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runselenium"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_selenium = pytest.mark.skip(reason="need --runselenium option to run")
    for item in items:
        if "selenium" in item.keywords:
            item.add_marker(skip_selenium)


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
