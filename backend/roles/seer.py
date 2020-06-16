'''
The Seer role
'''
import logging
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Seer",
    night_action=True,
    night_button_text="Select someone to check",
    day_text="""
You are a Seer! You get to check the identity of one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to check...
    """,
    vote_text=None,
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=DEFAULT_ROLE,
)


class SeerAction(GameAction):
    def execute(self, game):
        logging.warning("Seer action occurred but not written yet")


def register(role_map):
    role_map.update({
        PlayerRole.SEER: RoleDetails(description, SeerAction)
    })
