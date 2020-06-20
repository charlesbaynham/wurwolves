from uuid import uuid4 as uuid

import pytest

from backend.game import WurwolvesGame
from backend.model import GameStage

GAME_ID = "hot-potato"
USER_ID = uuid()


@pytest.fixture
def demo_game(db_session) -> WurwolvesGame:
    g = WurwolvesGame(GAME_ID)

    # You need at least three players for start_game() to work
    g.join(USER_ID)
    g.join(uuid())
    g.join(uuid())

    return g


def test_spectator_lobby(demo_game):
    assert hasattr(demo_game, "spectator_lobby_action")
    demo_game.spectator_lobby_action(USER_ID)
