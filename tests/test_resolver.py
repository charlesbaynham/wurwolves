import datetime
from unittest.mock import Mock
from uuid import uuid4 as uuid

import pytest

from backend.model import (ActionModel, GameModel, GameStage, PlayerModel,
                           PlayerRole, PlayerState, UserModel)
from backend.resolver import process_actions
from backend.roles.common import VillagerAction, WolfAction, SeerAction
from backend.roles.medic import MedicAction


@pytest.fixture
def wolf_medic_game_model():
    users = [
        UserModel(id=uuid(), name="Villager 1", name_is_generated=False),
        UserModel(id=uuid(), name="Villager 2", name_is_generated=False),
        UserModel(id=uuid(), name="Wolfy Mcwolfington", name_is_generated=False),
        UserModel(id=uuid(), name="Medic", name_is_generated=False),
    ]
    players = [
        PlayerModel(id=1, game_id=1, user_id=users[0].id, user=users[0],
                    role=PlayerRole.VILLAGER, state=PlayerState.ALIVE),
        PlayerModel(id=2, game_id=1, user_id=users[1].id, user=users[1],
                    role=PlayerRole.VILLAGER, state=PlayerState.ALIVE),
        PlayerModel(id=3, game_id=1, user_id=users[2].id, user=users[2],
                    role=PlayerRole.WOLF, state=PlayerState.ALIVE),
        PlayerModel(id=4, game_id=1, user_id=users[3].id, user=users[2],
                    role=PlayerRole.MEDIC, state=PlayerState.ALIVE),
    ]
    game = GameModel(
        id=1, created=datetime.datetime.now(), update_counter=1,
        stage=GameStage.NIGHT, players=players, messages=[]
    )
    actions = [
        # Wolf kills player 1
        ActionModel(id=1, game_id=1, player_id=3, stage_id=1,
                    selected_id=users[0].id, game=game, player=players[2]),
        # But medic saves player 1
        ActionModel(id=2, game_id=1, player_id=4, stage_id=1,
                    selected_id=users[0].id, game=game, player=players[3]),
    ]

    return {
        "players": players,
        "actions": actions,
        "game": game,
        "users": users,
    }


def test_actions_framework(wolf_medic_game_model):
    mock_game = Mock()
    mock_game.get_players_model.return_value = wolf_medic_game_model['players']
    mock_game.get_actions_model.return_value = wolf_medic_game_model['actions']

    VillagerAction.execute = Mock()
    WolfAction.execute = Mock()
    MedicAction.execute = Mock()
    SeerAction.execute = Mock()

    process_actions(mock_game)

    assert VillagerAction.execute.call_count == 0
    assert WolfAction.execute.call_count == 1
    assert MedicAction.execute.call_count == 1
    assert SeerAction.execute.call_count == 0
