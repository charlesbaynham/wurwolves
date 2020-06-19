"""
The Jester role

The jester wins by getting themselves lynched by the villagers
"""

from ..model import GameStage, PlayerRole
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails, StageAction

description = RoleDescription(
    display_name="Jester",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a Jester!

You win if you get yourself lynched by the villagers. 
    """
        )
    },
    team=RoleDescription.Team.JESTER,
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({PlayerRole.JESTER: RoleDetails(description)})
