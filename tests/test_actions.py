from unittest.mock import Mock
from uuid import uuid4 as uuid

import pytest
from fastapi import HTTPException

from backend.game import WurwolvesGame
from backend.model import PlayerRole, GameStage

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