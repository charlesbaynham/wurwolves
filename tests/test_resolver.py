import datetime
from unittest.mock import Mock
from unittest.mock import patch
from uuid import uuid4 as uuid

import pytest

from backend.model import ActionModel
from backend.model import GameModel
from backend.model import GameStage
from backend.model import PlayerModel
from backend.model import PlayerRole
from backend.model import PlayerState
from backend.model import UserModel


@pytest.fixture
def wolf_medic_game_model():
    users = [
        UserModel(id=uuid(), name="Villager 1", name_is_generated=False),
        UserModel(id=uuid(), name="Villager 2", name_is_generated=False),
        UserModel(id=uuid(), name="Wolfy Mcwolfington", name_is_generated=False),
        UserModel(id=uuid(), name="Medic", name_is_generated=False),
    ]
    players = [
        PlayerModel(
            id=1,
            game_id=1,
            user_id=users[0].id,
            user=users[0],
            role=PlayerRole.VILLAGER,
            state=PlayerState.ALIVE,
        ),
        PlayerModel(
            id=2,
            game_id=1,
            user_id=users[1].id,
            user=users[1],
            role=PlayerRole.VILLAGER,
            state=PlayerState.ALIVE,
        ),
        PlayerModel(
            id=3,
            game_id=1,
            user_id=users[2].id,
            user=users[2],
            role=PlayerRole.WOLF,
            state=PlayerState.ALIVE,
        ),
        PlayerModel(
            id=4,
            game_id=1,
            user_id=users[3].id,
            user=users[3],
            role=PlayerRole.MEDIC,
            state=PlayerState.ALIVE,
        ),
    ]
    game = GameModel(
        id=1,
        update_tag=1,
        stage=GameStage.NIGHT,
        stage_id=1,
        players=players,
        messages=[],
        num_attempts_this_stage=0,
    )
    actions = [
        # Wolf kills player 1
        ActionModel(
            id=1,
            game_id=1,
            player_id=3,
            stage_id=1,
            game=game,
            player=players[2],
            selected_player_id=players[0].id,
            selected_player=players[0],
            stage=GameStage.NIGHT,
        ),
        # But medic saves player 1
        ActionModel(
            id=2,
            game_id=1,
            player_id=4,
            stage_id=1,
            game=game,
            player=players[3],
            selected_player_id=players[0].id,
            selected_player=players[0],
            stage=GameStage.NIGHT,
        ),
    ]

    return {
        "players": players,
        "actions": actions,
        "game": game,
        "users": users,
    }


@pytest.fixture
def wolf_medic_seer_game_model(wolf_medic_game_model):
    users = wolf_medic_game_model["users"]
    players = wolf_medic_game_model["players"]
    game = wolf_medic_game_model["game"]
    actions = wolf_medic_game_model["actions"]

    seer_user = UserModel(id=uuid(), name="Seer", name_is_generated=False)
    seer_player = PlayerModel(
        id=5,
        game_id=1,
        user_id=seer_user.id,
        user=seer_user,
        role=PlayerRole.SEER,
        state=PlayerState.ALIVE,
    )
    # Seer checks the wolf
    seer_action = ActionModel(
        id=3,
        game_id=1,
        stage_id=1,
        game=game,
        player_id=seer_player.id,
        player=seer_player,
        selected_player_id=players[2].id,
        selected_player=players[2],
        stage=GameStage.NIGHT,
    )

    users.append(seer_user)
    players.append(seer_player)
    actions.append(seer_action)

    game.players = players

    return {
        "players": players,
        "actions": actions,
        "game": game,
        "users": users,
    }


@patch("backend.roles.medic.MedicAction.execute")
@patch("backend.roles.wolf.WolfAction.execute")
@patch("backend.roles.seer.SeerAction.execute")
def test_actions_framework(m1, m2, m3, wolf_medic_game_model):
    from backend.resolver import process_actions
    import backend.roles.medic as medic
    import backend.roles.wolf as wolf
    import backend.roles.seer as seer

    mock_game_model = Mock()
    mock_game_model.stage = GameStage.NIGHT
    mock_game_model.stage_id = 1

    mock_game = Mock()
    mock_game.get_game_model.return_value = mock_game_model
    mock_game.get_players_model.return_value = wolf_medic_game_model["players"]
    mock_game.get_actions_model.return_value = wolf_medic_game_model["actions"]

    process_actions(mock_game, mock_game_model.stage, mock_game_model.stage_id)

    assert wolf.WolfAction.execute.call_count == 1
    assert medic.MedicAction.execute.call_count == 1
    assert seer.SeerAction.execute.call_count == 0


def test_actions_chat(wolf_medic_seer_game_model):
    from backend.resolver import process_actions

    mock_game_model = Mock()
    mock_game_model.stage = GameStage.NIGHT
    mock_game_model.stage_id = 1

    mock_game = Mock()
    mock_game.get_game_model.return_value = mock_game_model
    mock_game.get_players_model.return_value = wolf_medic_seer_game_model["players"]
    mock_game.get_actions_model.return_value = wolf_medic_seer_game_model["actions"]

    process_actions(mock_game, mock_game_model.stage, mock_game_model.stage_id)

    assert mock_game.send_chat_message.call_count >= 1
