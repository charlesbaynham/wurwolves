'''
The Wolf role
'''
import logging
from ..model import PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails, ActionMixin
from .medic import CancelledByMedic


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
    team=RoleDescription.Team.WOLVES,
    fallback_role=DEFAULT_ROLE,
)


class CancelledByWolf(ActionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancelled_by_wolf = False

        self.bind_as_modifier(self.__do_mod, __class__, WolfAction, True)

    def __do_mod(self):
        self.cancelled_by_wolf = True


class WolfAction(GameAction, CancelledByMedic):
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

        if self.cancelled_by_medic:
            logging.warning("Wolf attacked but the medic saved")
        else:
            logging.warning("Wolf attacked successfully")


def register(role_map):
    role_map.update({
        PlayerRole.WOLF: RoleDetails(description, WolfAction)
    })
