import os

import pytest

from backend.model import GameEvent, GameEventVisibility, EventType


TESTING_DB_URL = "sqlite:///testing.db"


@pytest.fixture(scope="session")
def engine():
    os.environ['DATABASE_URL'] = TESTING_DB_URL

    from backend.database import engine

    return engine


@pytest.fixture
def session(engine):
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


def test_fixtures(session):
    assert len(session.query(GameEvent).all()) == 0
    assert len(session.query(GameEventVisibility).all()) == 0


def test_storage(session):
    session.add(GameEvent(game_id=123456, event_type=EventType.GUI))
    session.commit()

    assert session.query(GameEvent.game_id).first()[0] == 123456
