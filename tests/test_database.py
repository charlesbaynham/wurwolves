from backend.model import GameEvent, GameEventVisibility, EventType


def test_fixtures(db_session):
    assert len(db_session.query(GameEvent).all()) == 0
    assert len(db_session.query(GameEventVisibility).all()) == 0


def test_storage(db_session):
    db_session.add(GameEvent(game_id=123456, event_type=EventType.GUI))
    db_session.commit()

    assert db_session.query(GameEvent.game_id).first()[0] == 123456
