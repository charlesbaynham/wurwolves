import logging
import random as rd
from unittest.mock import Mock
from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi import HTTPException

from backend.game import WurwolvesGame
from backend.model import GameStage
from backend.model import PlayerRole
from backend.model import PlayerState


def setup_module(module):
    rd.seed(123)


def uuid():
    return UUID(int=rd.getrandbits(128))


GAME_ID = "hot-potato"
USER_ID = UUID("610e4ad5-09c4-7055-dff4-948fe6b4f832")


@pytest.fixture
def demo_game(db_session) -> WurwolvesGame:
    g = WurwolvesGame(GAME_ID)

    # You need at least three players for start_game() to work
    ids = [USER_ID, uuid(), uuid()]
    for i, id in enumerate(ids):
        g.join(id)
        g.set_user_name(id, f"Player {i}")

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
            demo_game.wolf_night_action(player.user_id, player.user_id)


def test_medic_night(demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    assert hasattr(demo_game, "medic_night_action")

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id, player.user_id)


def test_medic_forbidden_wolf(demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    assert hasattr(demo_game, "medic_night_action")

    for player in players:
        if player.role == PlayerRole.MEDIC:
            with pytest.raises(HTTPException):
                demo_game.wolf_night_action(player.user_id)


@patch("backend.resolver.process_actions")
def test_actions_processed_with_spectator(resolver_mock, demo_game, caplog):
    caplog.set_level(logging.DEBUG)

    demo_game.start_game()

    demo_game.join(uuid())

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id, player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id, player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_night_action(player.user_id, player.user_id)

    resolver_mock.assert_called_once()


def test_actions_update_state(demo_game):
    demo_game.start_game()

    demo_game.process_actions = Mock(unsafe=True)

    players = demo_game.get_players_model()

    old_game_hash = demo_game.get_hash_now()

    num_calls = 0
    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id, player.user_id)
            num_calls += 1

    new_game_hash = demo_game.get_hash_now()

    assert num_calls == 1
    assert old_game_hash != new_game_hash


@patch("backend.resolver.process_actions")
def test_actions_processed(resolver_mock, demo_game):
    demo_game.start_game()

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id, player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id, player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_night_action(player.user_id, player.user_id)

    resolver_mock.assert_called_once()


@patch("backend.resolver.process_actions")
def test_actions_processed_day(resolver_mock, demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.DAY)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_day_action(player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_day_action(player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_day_action(player.user_id)

    resolver_mock.assert_called_once()


def test_actions_processed_day_no_errors(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.DAY)
    assert demo_game.get_game_model().stage == GameStage.DAY

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_day_action(player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_day_action(player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_day_action(player.user_id)

    assert demo_game.get_game_model().stage == GameStage.VOTING


def test_actions_processed_night_wolfing(demo_game):
    demo_game.start_game()

    assert demo_game.get_game_model().stage == GameStage.NIGHT

    players = demo_game.get_players_model()

    lucky = players[0].user.id
    unlucky = players[1].user.id

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id, lucky)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id, unlucky)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_night_action(player.user_id, unlucky)

    assert demo_game.get_player_model(unlucky).state == PlayerState.WOLFED


def test_actions_processed_voting_no_errors(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.VOTING)
    assert demo_game.get_game_model().stage == GameStage.VOTING

    players = demo_game.get_players_model()

    the_dick = players[0].user_id

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_voting_action(player.user_id, the_dick)


def test_actions_processed_voting_results(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.VOTING)
    assert demo_game.get_game_model().stage == GameStage.VOTING

    players = demo_game.get_players_model()

    the_dick = players[0].user_id

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_voting_action(player.user_id, the_dick)

    assert demo_game.get_player_model(the_dick).state == PlayerState.LYNCHED


def test_no_voting_dead_people(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.VOTING)
    assert demo_game.get_game_model().stage == GameStage.VOTING

    players = demo_game.get_players_model()

    the_dick = players[0].user_id
    demo_game.set_player_state(demo_game.get_player_id(the_dick), PlayerState.WOLFED)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            with pytest.raises(HTTPException):
                demo_game.medic_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.WOLF:
            with pytest.raises(HTTPException):
                demo_game.wolf_voting_action(player.user_id, the_dick)
        elif player.role == PlayerRole.SEER:
            with pytest.raises(HTTPException):
                demo_game.seer_voting_action(player.user_id, the_dick)


def test_no_night_action_on_dead_people(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.NIGHT)
    assert demo_game.get_game_model().stage == GameStage.NIGHT

    players = demo_game.get_players_model()

    the_dick = players[0].user_id
    demo_game.set_player_state(demo_game.get_player_id(the_dick), PlayerState.WOLFED)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            with pytest.raises(HTTPException):
                demo_game.medic_night_action(player.user_id, the_dick)
        elif player.role == PlayerRole.WOLF:
            with pytest.raises(HTTPException):
                demo_game.wolf_night_action(player.user_id, the_dick)
        elif player.role == PlayerRole.SEER:
            with pytest.raises(HTTPException):
                demo_game.seer_night_action(player.user_id, the_dick)


def test_action_preventable(demo_game):
    demo_game.start_game()

    def do_medic():
        for player in demo_game.get_players_model():
            if player.role == PlayerRole.MEDIC:
                demo_game.medic_night_action(player.user_id, player.user_id)

    demo_game._set_stage(GameStage.NIGHT)
    do_medic()

    demo_game._set_stage(GameStage.NIGHT)

    with patch(
        "backend.roles.medic.MedicAction.is_action_available", return_value=False
    ):
        with pytest.raises(HTTPException):
            do_medic()
