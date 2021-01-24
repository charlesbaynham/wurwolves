from uuid import uuid4 as uuid

import pytest

from backend.game import WurwolvesGame
from backend.model import GameStage
from backend.model import PlayerState

GAME_ID = "hot-potato"
USER_ID = uuid()


@pytest.fixture
def demo_game(demo_game_maker) -> WurwolvesGame:
    return demo_game_maker(3)


@pytest.fixture
def demo_game_maker(db_session):
    def func(num_players):
        import random

        random.seed(123)

        g = WurwolvesGame(GAME_ID)

        # You need at least three players for start_game() to work
        g.join(USER_ID)

        for _ in range(num_players - 1):
            g.join(uuid())

        return g

    return func


def test_parse(db_session, demo_game):
    WurwolvesGame(GAME_ID).parse_game_to_state(USER_ID)


def test_parse_spectator(db_session, demo_game):
    state = WurwolvesGame(GAME_ID).parse_game_to_state(USER_ID)

    json = state.json()

    assert "Welcome to Wurwolves" in json
    assert "Spectator" in state.controls_state.title
    assert state.stage == GameStage.LOBBY
    assert state.controls_state.button_enabled


def test_parse_player(db_session, demo_game):
    demo_game.start_game()

    state = WurwolvesGame(GAME_ID).parse_game_to_state(USER_ID)

    assert state.stage == GameStage.NIGHT
    assert "Spectator" not in state.controls_state.title


def test_parse_new_spectator(db_session, demo_game):
    demo_game.start_game()

    u = uuid()
    demo_game.join(u)

    state = WurwolvesGame(GAME_ID).parse_game_to_state(u)

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
    dead_state = WurwolvesGame(GAME_ID).parse_game_to_state(USER_ID)
    alive_state = WurwolvesGame(GAME_ID).parse_game_to_state(other_player)

    assert not dead_state.controls_state.button_visible
    assert alive_state.controls_state.button_visible


def test_parse_speed(demo_game_maker):

    num_players = 10
    num_repeats = 10

    demo_game = demo_game_maker(num_players)

    users = [p.user_id for p in demo_game.get_game_model().players]

    import timeit

    def f():
        for u in users:
            state = WurwolvesGame(GAME_ID).parse_game_to_state(u)

    out = timeit.timeit(f, number=num_repeats)

    time_per_render = out / (num_players * num_repeats)

    assert time_per_render < 0.2
