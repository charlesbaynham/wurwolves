"""
The Jester role

The jester wins by getting themselves lynched by the villagers
"""

from ..model import GameStage, PlayerRole
from .common import RoleDescription, RoleDetails, StageAction
from .villager import description as villager
from .teams import Team

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


def register(role_map):
    role_map.update({PlayerRole.JESTER: RoleDetails(role_description=description)})
