'''
The Medic role

The Medic can save one person every night. 
'''
import logging

from ..model import PlayerRole
from ..resolver import ActionMixin, GameAction
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails

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
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=DEFAULT_ROLE,
)


class AffectedByMedic(ActionMixin):
    '''
    Creates attributes `target_saved_by_medic` and `originator_saved_by_medic`
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_saved_by_medic = False
        self.originator_saved_by_medic = False

        self.bind_as_modifier(self.__orig_saved, __class__, MedicAction, True)
        self.bind_as_modifier(self.__target_saved, __class__, MedicAction, False)

    def __orig_saved(self):
        self.originator_saved_by_medic = True

    def __target_saved(self):
        self.target_saved_by_medic = True


class MedicAction(GameAction):
    def execute(self, game):
        logging.warning("Medic action occurred but not written yet")


def register(role_map):
    role_map.update({
        PlayerRole.MEDIC: RoleDetails(description, MedicAction)
    })
