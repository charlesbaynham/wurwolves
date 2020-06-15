'''
The Wolf role
'''
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Wolf",
    night_action=True,
    day_text="""
You are a Wolf! You kill one person each night

You win if the wolves kill enough villager that you are equal in number
    """,
    night_text="""
Choose who to kill!
    """,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)


class WolfAction(GameAction):
    def execute(self, game):
        pass


def register(role_map):
    role_map.update({
        PlayerRole.WOLF: RoleDetails(description, WolfAction)
    })
