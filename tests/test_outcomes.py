from uuid import uuid4 as uuid

import pytest

from backend.database import session_scope
from backend.game import WurwolvesGame
from backend.model import GameStage, PlayerRole, PlayerState

GAME_ID = "Horse battery staple"


@pytest.fixture
def five_player_game(db_session) -> WurwolvesGame:

    g = WurwolvesGame(GAME_ID)

    # Make players
    user_ids = [uuid() for _ in range(5)]
    roles = [
        PlayerRole.WOLF,
        PlayerRole.MEDIC,
        PlayerRole.SEER,
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
    ]
    names = ["Wolf", "Medic", "Seer", "Villager 1", "Villager 2"]

    for i, id in enumerate(user_ids):
        g.join(id)

    g.start_game()

    # Override the roles
    with session_scope() as s:
        for id, role, name in zip(user_ids, roles, names):
            u = g.get_player(id)
            s.add(u)
            u.role = role
            g.set_user_name(id, name)

    roles_map = {name: user_id for name, user_id in zip(names, user_ids)}

    return g, roles_map


def test_setup(five_player_game):
    pass


def test_medic_save(five_player_game):
    game, roles_map = five_player_game

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Medic"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.ALIVE


def test_wolf_kill(five_player_game):
    game, roles_map = five_player_game

    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Wolf"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_player_model(roles_map["Medic"]).state == PlayerState.WOLFED


def test_wolf_win(five_player_game):
    game, roles_map = five_player_game

    # Kill a villager and the medic and see if wolves win
    game.set_player_state(roles_map["Villager 1"], PlayerState.LYNCHED)

    # Wolves get medic:
    game.wolf_night_action(roles_map["Wolf"], roles_map["Medic"])
    game.medic_night_action(roles_map["Medic"], roles_map["Wolf"])
    game.seer_night_action(roles_map["Seer"], roles_map["Medic"])

    assert game.get_game_model().stage == GameStage.ENDED
