"""
The Jester role

The jester wins by getting themselves lynched by the villagers
"""

from ..model import PlayerRole
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails

description = RoleDescription(
    display_name="Jester",
    night_action=False,
    day_text="""
You are a Jester!

You win if you get yourself lynched by the villagers. 
    """,
    team=RoleDescription.Team.JESTER,
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({PlayerRole.JESTER: RoleDetails(description, None)})
