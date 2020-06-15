'''
The Seer role
'''
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Seer",
    night_action=True,
    day_text="""
You are a Seer! You get to check the identity of one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to check...
    """,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)


class SeerAction(GameAction):
    def execute(self, game):
        pass


def register(role_map):
    role_map.update({
        PlayerRole.SEER: RoleDetails(description, SeerAction)
    })
