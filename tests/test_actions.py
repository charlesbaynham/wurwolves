from unittest.mock import Mock
from uuid import uuid4 as uuid

import pytest
from fastapi import HTTPException

from backend.game import WurwolvesGame
from backend.model import GameStage, PlayerRole, PlayerState

GAME_ID = "hot-potato"
USER_ID = uuid()


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


def test_actions_processed_with_spectator(demo_game):
    demo_game.start_game()

    demo_game.join(uuid())

    demo_game.process_actions = Mock(unsafe=True)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_night_action(player.user_id)

    demo_game.process_actions.assert_called_once()


def test_actions_processed(demo_game):
    demo_game.start_game()

    demo_game.process_actions = Mock(unsafe=True)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_night_action(player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_night_action(player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_night_action(player.user_id)

    demo_game.process_actions.assert_called_once()


def test_actions_processed_day(demo_game):
    demo_game.start_game()
    demo_game._set_stage(GameStage.DAY)

    demo_game.process_actions = Mock(unsafe=True)

    players = demo_game.get_players_model()

    for player in players:
        if player.role == PlayerRole.MEDIC:
            demo_game.medic_day_action(player.user_id)
        elif player.role == PlayerRole.WOLF:
            demo_game.wolf_day_action(player.user_id)
        elif player.role == PlayerRole.SEER:
            demo_game.seer_day_action(player.user_id)

    demo_game.process_actions.assert_called_once()


def test_actions_processed_day_noerrors(demo_game):
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
    assert demo_game.get_game_model().stage == GameStage.DAY


def test_actions_processed_voting_noerrors(demo_game):
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
    assert demo_game.get_game_model().stage == GameStage.NIGHT
