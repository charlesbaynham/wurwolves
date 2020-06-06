import os
import pytest

TESTING_DB_URL = "sqlite:///testing.db"

@pytest.fixture
def client():
    return None

@pytest.fixture(scope="session")
def engine():
    ''' Return an engine to the database.

    This fixture should not be used as the database is not cleaned between
    invocations. Use db_session instead. 
    '''
    os.environ['DATABASE_URL'] = TESTING_DB_URL

    from backend.database import engine

    return engine


@pytest.fixture
def db_session(engine):
    '''
    Get an SQLAlchemy database session to a clean database with the model schema
    set up. 
    '''
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
def api_client():
    '''
    Get a FastAPI TestClient pointing at the app 
    '''
    from fastapi.testclient import TestClient
    from backend.main import app

    return TestClient(app)
