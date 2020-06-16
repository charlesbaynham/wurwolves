'''
The Medic role

The Medic can save one person every night. 
'''
import logging
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails, ActionMixin


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


class CancelledByMedic(ActionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancelled_by_medic = False

        self.bind_as_modifier(self.__do_mod, __class__, MedicAction, False)

    def __do_mod(self):
        self.cancelled_by_medic = True


class MedicAction(GameAction):
    mixins_affecting_originators = []
    mixins_affecting_targets = []

    def do_modifiers(self):
        for MixinClass in self.mixins_affecting_originators:
            for action in self.target.originated_from:
                if isinstance(action, MixinClass):
                    f = getattr(action, ActionMixin.get_action_method_name(MixinClass))
                    f()
        for MixinClass in self.mixins_affecting_targets:
            for action in self.target.targetted_by:
                if isinstance(action, MixinClass):
                    f = getattr(action, ActionMixin.get_action_method_name(MixinClass))
                    f()

    def execute(self, game):
        logging.warning("Medic action occurred but not written yet")


def register(role_map):
    role_map.update({
        PlayerRole.MEDIC: RoleDetails(description, MedicAction)
    })
