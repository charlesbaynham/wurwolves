'''
The Wolf role
'''
import logging

from ..model import PlayerRole
from ..resolver import ActionMixin, GameAction
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails
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
    def execute(self, game):
        target_name = self.target.model.user.name

        if self.cancelled_by_medic:
            game.send_chat_message(
                f"{target_name} was attacked but survived!",
                is_strong=True
            )
        else:
            game.send_chat_message(
                f"{target_name} was brutally murdered",
                is_strong=True
            )


def register(role_map):
    role_map.update({
        PlayerRole.WOLF: RoleDetails(description, WolfAction)
    })
