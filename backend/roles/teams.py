from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game import WurwolvesGame
from ..model import PlayerState


class Team(Enum):
    VILLAGERS = "VILLAGERS"
    WOLVES = "WOLVES"
    SPECTATORS = "SPECTATORS"
    JESTER = "JESTER"


def team_has_won(game: "WurwolvesGame", team: Team) -> bool:
    from .registration import get_role_team

    players = game.get_players_model()

    num_alive_villagers = 0

    for player in players:
        team = get_role_team(player.role)
        if team == Team.VILLAGERS and player.state == PlayerState.ALIVE:
            num_alive_villagers += 1

    return False


def win_ends_game(team: Team) -> bool:
    return True
