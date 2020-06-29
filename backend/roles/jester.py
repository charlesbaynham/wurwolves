"""
The Jester role

The jester wins by getting themselves lynched by the villagers
"""

import logging
from typing import TYPE_CHECKING

from ..model import GameStage, PlayerRole
from .common import RoleDescription, RoleDetails, StageAction
from .teams import Team
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


description = RoleDescription(
    display_name="Jester",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a Jester!

You win if you get yourself lynched by the villagers. 
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
You win if you get yourself lynched by the villagers. 

You have nothing to do at night. Plot your jesting. 
    """
        ),
    },
    team=Team.JESTER,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


def announce_to_wolves(game: "WurwolvesGame"):
    logging.warning("jester announce to wolves")

    jester = game.get_players_model(role=PlayerRole.JESTER)

    if jester:
        wolves = game.get_players_model(role=PlayerRole.WOLF)

        game.send_chat_message(
            "There's a jester in the game: it's {}".format(jester.user.name),
            is_strong=True,
            player_list=[p.id for p in wolves],
        )


def register(role_map):
    role_map.update(
        {PlayerRole.JESTER: RoleDetails(role_description=description)},
        startup_callback=announce_to_wolves,
    )
