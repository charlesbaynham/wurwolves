import logging
from enum import Enum
from typing import TYPE_CHECKING

from ..model import PlayerState

if TYPE_CHECKING:
    from ..game import WurwolvesGame


class Team(Enum):
    VILLAGERS = "VILLAGERS"
    WOLVES = "WOLVES"
    SPECTATORS = "SPECTATORS"
    JESTER = "JESTER"


def villagers_won(game):
    from .registration import get_role_team

    players = game.get_players_model()

    num_alive_villagers = 0
    num_alive_wolves = 0

    for player in players:
        team = get_role_team(player.role)
        if team == Team.VILLAGERS and player.state == PlayerState.ALIVE:
            num_alive_villagers += 1
        if team == Team.WOLVES and player.state == PlayerState.ALIVE:
            num_alive_wolves += 1

    return num_alive_wolves == 0


def wolves_won(game):
    from .registration import get_role_team

    players = game.get_players_model()

    num_alive_villagers = 0
    num_alive_wolves = 0

    for player in players:
        team = get_role_team(player.role)
        if team == Team.VILLAGERS and player.state == PlayerState.ALIVE:
            num_alive_villagers += 1
        if team == Team.WOLVES and player.state == PlayerState.ALIVE:
            num_alive_wolves += 1

    return num_alive_wolves >= num_alive_villagers


def jester_won(game):
    from .registration import get_role_team

    players = game.get_players_model()

    jester_in_game = False
    jester_voted_off = False

    for player in players:
        team = get_role_team(player.role)
        if team == Team.JESTER:
            jester_in_game = True
            if player.state == PlayerState.LYNCHED:
                jester_voted_off = True

    return jester_in_game and jester_voted_off


win_map = {
    Team.WOLVES: wolves_won,
    Team.VILLAGERS: villagers_won,
    Team.JESTER: jester_won,
    Team.SPECTATORS: lambda _: False,
}


def team_has_won(game: "WurwolvesGame", team: Team) -> bool:
    return win_map[team](game)


def win_ends_game(team: Team) -> bool:
    return team != Team.JESTER


def win_action(game: "WurwolvesGame", team: Team):
    logging.info(f"Team {team} has won!")
