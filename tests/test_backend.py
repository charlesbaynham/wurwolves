from backend.game import WurwolvesGame
from backend.model import GameEvent, GameEventVisibility, EventType, hash_game_id
from backend.events import EventQueue
from uuid import uuid4 as uuid


GAME_ID = "hot-potato"
USER_ID = uuid()


def test_client(client):
    pass


def test_read_main(api_client):
    response = api_client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello world!"}


def test_add_player(api_client, db_session):
    game = WurwolvesGame(game_id=GAME_ID, user_id=USER_ID)
    game.add_player("Charles")

    assert (db_session
            .query(GameEvent)
            .filter(GameEvent.game_id == hash_game_id(GAME_ID))
            .filter(GameEvent.event_type == EventType.NEW_PLAYER)
            ).count() == 1

    assert (db_session
            .query(GameEvent)
            .filter(GameEvent.game_id == hash_game_id(GAME_ID))
            .filter(GameEvent.event_type == EventType.GUI)
            ).count() == 1

    game.add_player("Gaby")

    assert (db_session
            .query(GameEvent)
            .filter(GameEvent.game_id == hash_game_id(GAME_ID))
            .filter(GameEvent.event_type == EventType.GUI)
            ).count() == 2

    assert all(
        db_session
        .query(GameEvent.public_visibility)
        .filter(GameEvent.game_id == hash_game_id(GAME_ID))
        .filter(GameEvent.event_type == EventType.GUI)
        .all()
    )

    q = EventQueue(GAME_ID)