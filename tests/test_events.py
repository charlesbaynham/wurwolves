import pytest

from backend.model import EventType, GameEvent, GameEventVisibility, hash_game_id
from uuid import uuid4 as uuid

from backend.events import EventQueue


GAME_ID = "hot-potato"
USER_ID = uuid()


@pytest.fixture()
def fake_events(db_session):
    # Add a public event
    db_session.add(GameEvent(
        game_id=hash_game_id(GAME_ID),
        event_type=EventType.GUI,
        details={},
        public_visibility=True,
    ))

    # Add a user-only event
    g = GameEvent(
        game_id=hash_game_id(GAME_ID),
        event_type=EventType.CHAT,
        details={},
        public_visibility=False,
    )

    g.users_with_visibility.append(GameEventVisibility(user_id=USER_ID))

    db_session.add(g)

    # Add a secret event
    db_session.add(GameEvent(
        game_id=hash_game_id(GAME_ID),
        event_type=EventType.NEW_PLAYER,
        details={},
        public_visibility=False,
    ))

    db_session.commit()


def test_get_all_events(db_session, fake_events):
    q_public = EventQueue(GAME_ID, public_only=True)
    q_user = EventQueue(GAME_ID, user_ID=USER_ID)
    q_secrets = EventQueue(GAME_ID, public_only=False)

    assert len(q_public.get_all_events()) == 1
    assert len(q_user.get_all_events()) == 2
    assert len(q_secrets.get_all_events()) == 3


def test_latest_event(db_session, fake_events):
    q_public = EventQueue(GAME_ID, public_only=True)
    q_user = EventQueue(GAME_ID, user_ID=USER_ID)
    q_secrets = EventQueue(GAME_ID, public_only=False)

    assert q_public.get_latest_event_id() == 1
    assert q_user.get_latest_event_id() == 2
    assert q_secrets.get_latest_event_id() == 3


def test_since(db_session, fake_events):
    q_public = EventQueue(GAME_ID, public_only=True)
    q_user = EventQueue(GAME_ID, user_ID=USER_ID)
    q_secrets = EventQueue(GAME_ID, public_only=False)

    assert len(q_public.get_all_events(since=2)) == 0
    assert len(q_user.get_all_events(since=2)) == 0
    assert len(q_secrets.get_all_events(since=2)) == 1


def test_event_filter(db_session, fake_events):
    q_all = EventQueue(GAME_ID)
    q_gui = EventQueue(GAME_ID, type_filter=EventType.GUI)
    q_gui_or_player = EventQueue(GAME_ID, type_filter=[EventType.GUI, EventType.NEW_PLAYER])

    assert len(q_all.get_all_events()) == 3
    assert len(q_gui.get_all_events()) == 1
    assert len(q_gui_or_player.get_all_events()) == 2
