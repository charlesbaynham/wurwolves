

from uuid import uuid4 as uuid

from backend.model import EventType
from backend.events import EventQueue
from backend.game import WurwolvesGame

GAME_ID = "hot-potato"
USER_ID = uuid()


def test_add_player(db_session):
    g = WurwolvesGame(GAME_ID, USER_ID)
    g.set_player("Charles")

    assert len(EventQueue(
        GAME_ID,
        type_filter=EventType.UPDATE_PLAYER
    ).get_all_events()) == 1

    g.set_player("Gaby")

    assert len(EventQueue(
        GAME_ID,
        type_filter=EventType.UPDATE_PLAYER
    ).get_all_events()) == 2
