"""
The Acolyte role

The acolyte has no special powers but wins if the wolves win. The wolves know who they are, but the acolyte
doesn't know anything. For the sake of the game's conclusion, the Acolyte counts as a villager.
"""
from ..model import GameStage
from ..model import PlayerRole
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .teams import Team
from .villager import description as villager

general_desc = """
You really like the idea of the werewolves, but you don't know who they are. Still, do your best to help
them out and sow confusion among the villagers.

You don't have any special powers.
You win if all the wolves win.
"""

description = RoleDescription(
    display_name="You are the Acolyte",
    stages={
        GameStage.NIGHT: StageAction(
            text=general_desc,
        ),
        GameStage.DAY: StageAction(text=general_desc),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


def register(role_map):
    role_map.update(
        {PlayerRole.ACOLYTE: RoleDetails(role_description=description, actions={})}
    )
