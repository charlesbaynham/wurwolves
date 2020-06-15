'''
The Wolf role
'''
import logging
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Wolf",
    night_action=True,
    night_button_text="Select someone to maul",
    day_text="""
You are a Wolf! You kill one person each night

You win if the wolves kill enough villagers that you are equal in number
    """,
    night_text="""
Choose who to kill!
    """,
    vote_text=None,
    fallback_role=DEFAULT_ROLE,
)


class WolfAction(GameAction):
    def execute(self, game):
        logging.warning("Wolf action occurred but not written yet")


def register(role_map):
    role_map.update({
        PlayerRole.WOLF: RoleDetails(description, WolfAction)
    })
