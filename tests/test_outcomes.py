from uuid import uuid4 as uuid

import pytest

from backend.database import session_scope
from backend.game import WurwolvesGame
from backend.model import PlayerRole, PlayerState

GAME_ID = "Horse battery staple"


@pytest.fixture
def six_player_game(db_session) -> WurwolvesGame:

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
    names = ["Wolfy 1", "Medic", "Seer", "Boring Dave", "Boring Jess"]

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

    roles_map = {role: user_id for role, user_id in zip(roles, user_ids)}

    return g, roles_map


def test_setup(six_player_game):
    pass


def test_medic_save(six_player_game):
    game, roles_map = six_player_game

    game.wolf_night_action(roles_map[PlayerRole.WOLF], roles_map[PlayerRole.MEDIC])
    game.medic_night_action(roles_map[PlayerRole.MEDIC], roles_map[PlayerRole.MEDIC])
    game.seer_night_action(roles_map[PlayerRole.SEER], roles_map[PlayerRole.MEDIC])

    assert game.get_player_model(roles_map[PlayerRole.MEDIC]).state == PlayerState.ALIVE


def test_wolf_kill(six_player_game):
    game, roles_map = six_player_game

    game.wolf_night_action(roles_map[PlayerRole.WOLF], roles_map[PlayerRole.MEDIC])
    game.medic_night_action(roles_map[PlayerRole.MEDIC], roles_map[PlayerRole.WOLF])
    game.seer_night_action(roles_map[PlayerRole.SEER], roles_map[PlayerRole.MEDIC])

    assert (
        game.get_player_model(roles_map[PlayerRole.MEDIC]).state == PlayerState.WOLFED
    )
