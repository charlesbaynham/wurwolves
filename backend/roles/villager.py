'''
The Villager role
'''
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Villager",
    night_action=False,
    day_text="""
You are a Villager. You have no special powers but you're special anyway. 

You win if all the wolves are eliminated. 
    """,
    night_text=None,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({
        PlayerRole.VILLAGER: RoleDetails(description, None)
    })
