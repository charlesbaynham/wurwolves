from uuid import uuid4 as uuid

import pytest
from fastapi import HTTPException

from backend.game import WurwolvesGame
from backend.model import PlayerRole

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


def test_wolf_night(demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    assert hasattr(demo_game, "wolf_night_action")

    for player in players:
        if player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id)


def test_medic_night(demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    assert hasattr(demo_game, "medic_night_action")

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id)


def test_medic_forbidden_wolf(demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    assert hasattr(demo_game, "medic_night_action")

    for player in players:
        if player.role == PlayerRole.MEDIC:
            with pytest.raises(HTTPException):
                demo_game.wolf_night_action(player.user_id)
