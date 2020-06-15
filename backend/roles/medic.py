'''
The Medic role

The Medic can save one person every night. 
'''
import logging
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Medic",
    night_action=True,
    night_button_text="Select someone to save",
    day_text="""
You are a medic! You get to save one person each night. 

You win if all the wolves are eliminated. 
    """,
    night_text="""
Choose who to save...
    """,
    fallback_role=DEFAULT_ROLE,
)


class MedicAction(GameAction):
    def execute(self, game):
        logging.warning("Medic action occurred but not written yet")


def register(role_map):
    role_map.update({
        PlayerRole.MEDIC: RoleDetails(description, MedicAction)
    })
