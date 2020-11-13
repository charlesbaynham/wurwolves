import logging
from enum import Enum
from typing import TYPE_CHECKING

from ..model import PlayerRole
from ..model import PlayerState

if TYPE_CHECKING:
    from ..game import WurwolvesGame


class Team(Enum):
    VILLAGERS = "villagers"
    WOLVES = "wolves"
    SPECTATORS = "spectators"
    JESTER = "jester"
    NARRATOR = "narrator"


def villagers_won(game):
    num_alive_wolves = number_of(game, Team.WOLVES, PlayerState.ALIVE)

    return num_alive_wolves == 0


def wolves_won(game):
    num_alive_villagers = number_of(game, Team.VILLAGERS, PlayerState.ALIVE)
    num_alive_jesters = number_of(game, Team.JESTER, PlayerState.ALIVE)
    num_alive_wolves = number_of(game, Team.WOLVES, PlayerState.ALIVE)

    return num_alive_wolves >= num_alive_villagers + num_alive_jesters


def number_of(game, team: Team, state: PlayerState):
    from .registration import get_role_team

    num = 0

    players = game.get_players_model()
    for player in players:
        player_team = get_role_team(player.role)
        if player_team == team and player.state == state:
            num += 1

    return num


def jester_won(game):
    num_lynched_jester = number_of(game, Team.JESTER, PlayerState.LYNCHED)

    return bool(num_lynched_jester)


win_map = {
    Team.WOLVES: wolves_won,
    Team.VILLAGERS: villagers_won,
    Team.JESTER: jester_won,
    Team.SPECTATORS: lambda _: False,
    Team.NARRATOR: lambda _: False,
}

if any(team not in win_map for team in list(Team)):
    raise TypeError("Not all teams are in the win_map")


def team_has_won(game: "WurwolvesGame", team: Team) -> bool:
    return win_map[team](game)


def win_ends_game(team: Team) -> bool:
    return team != Team.JESTER


def win_action(game: "WurwolvesGame", team: Team):
    from .registration import get_role_team

    logging.info(f"Team {team} has won!")
    if win_ends_game(team):
        game.send_chat_message(
            f"The game is ended and the {team.value} have won!", is_strong=True
        )
        # if team == Team.WOLVES:
        #     for player in game.get_players_model():
        #         if (
        #             get_role_team(player.role) == Team.VILLAGERS
        #             and player.state == PlayerState.ALIVE
        #             and player.role != PlayerRole.ACOLYTE
        #         ):
        #             game.kill_player(player.id, PlayerState.WOLFED)
    else:
        players_in_team = [
            p.id for p in game.get_players_model() if get_role_team(p.role) == team
        ]
        game.send_chat_message(
            "You have won! But the game isn't over...",
            is_strong=True,
            player_list=players_in_team,
        )
