from uuid import uuid4 as uuid

import pytest

from backend.frontend_parser import parse_game_to_state
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


def test_parse(db_session, demo_game):
    parse_game_to_state(demo_game, USER_ID)


def test_parse_spectator(db_session, demo_game):
    state = parse_game_to_state(demo_game, USER_ID)

    json = state.json()

    assert "Welcome to Wurwolves" in json
    assert "Spectator" in state.controls_state.title
    assert state.stage == GameStage.LOBBY
    assert state.controls_state.button_enabled


def test_parse_player(db_session, demo_game):
    demo_game.start_game()

    state = parse_game_to_state(demo_game, USER_ID)

    assert state.stage == GameStage.NIGHT
    assert "Spectator" not in state.controls_state.title


def test_parse_new_spectator(db_session, demo_game):
    demo_game.start_game()

    u = uuid()
    demo_game.join(u)

    state = parse_game_to_state(demo_game, u)

    assert "You're not playing" in state.controls_state.text
    assert "Spectator" in state.controls_state.title
    assert state.stage == GameStage.NIGHT
    assert not state.controls_state.button_enabled
