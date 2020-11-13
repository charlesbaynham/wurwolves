from uuid import uuid4 as uuid

import pytest

from backend.frontend_parser import parse_game_to_state
from backend.game import WurwolvesGame
from backend.model import GameStage
from backend.model import PlayerState

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
    parse_game_to_state(GAME_ID, USER_ID)


def test_parse_spectator(db_session, demo_game):
    state = parse_game_to_state(GAME_ID, USER_ID)

    json = state.json()

    assert "Welcome to Wurwolves" in json
    assert "Spectator" in state.controls_state.title
    assert state.stage == GameStage.LOBBY
    assert state.controls_state.button_enabled


def test_parse_player(db_session, demo_game):
    demo_game.start_game()

    state = parse_game_to_state(GAME_ID, USER_ID)

    assert state.stage == GameStage.NIGHT
    assert "Spectator" not in state.controls_state.title


def test_parse_new_spectator(db_session, demo_game):
    demo_game.start_game()

    u = uuid()
    demo_game.join(u)

    state = parse_game_to_state(GAME_ID, u)

    assert "You're not playing" in state.controls_state.text
    assert "Spectator" in state.controls_state.title
    assert state.stage == GameStage.NIGHT


def test_no_vote_dead(demo_game):

    demo_game.join(uuid())
    demo_game.join(uuid())

    other_player = uuid()
    demo_game.join(other_player)

    demo_game.start_game()

    # add a narrator too
    narrator_id = uuid()
    demo_game.join(narrator_id)
    demo_game.spectator_night_action(narrator_id)

    # 6 player game

    # Kill one of the players and set to VOTING
    player = demo_game.get_player_model(USER_ID)
    demo_game.kill_player(player.id, PlayerState.LYNCHED)
    demo_game._set_stage(GameStage.VOTING)

    # Ensure that the dead player can't see the vote button
    dead_state = parse_game_to_state(GAME_ID, USER_ID)
    alive_state = parse_game_to_state(GAME_ID, other_player)

    assert not dead_state.controls_state.button_visible
    assert alive_state.controls_state.button_visible
