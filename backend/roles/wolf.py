"""
The Wolf role
"""
import logging

from ..model import GameStage, PlayerRole
from ..resolver import ActionMixin, GameAction
from .common import RoleDescription, RoleDetails, StageAction
from .medic import AffectedByMedic
from .villager import description as villager

description = RoleDescription(
    display_name="Wolf",
    stages={
        GameStage.NIGHT: StageAction(
            text="""
You are a Wolf! You kill one person each night

You win if the wolves kill enough villagers that you are equal in number
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
Choose who to kill!
    """,
            button_text="Select someone to maul",
        ),
    },
    team=RoleDescription.Team.WOLVES,
    fallback_role=villager,
)


class AffectedByWolves(AffectedByMedic):
    """
    Creates attributes `originator_attacked_by_wolf` and `target_attacked_by_wolf`. 
    These can be cancelled by medic action
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.originator_attacked_by_wolf = False
        self.target_attacked_by_wolf = False

        self.bind_as_modifier(self.__orig_attacked, __class__, WolfAction, True)
        self.bind_as_modifier(self.__target_attacked, __class__, WolfAction, False)

    def __orig_attacked(self):
        if not self.originator_saved_by_medic:
            self.originator_attacked_by_wolf = True

    def __target_attacked(self):
        if not self.target_saved_by_medic:
            self.target_attacked_by_wolf = True


class WolfAction(GameAction, AffectedByMedic):
    def execute(self, game):
        target_name = self.target.model.user.name

        if self.target_saved_by_medic:
            game.send_chat_message(
                f"{target_name} was attacked but survived!", is_strong=True
            )
        else:
            game.send_chat_message(
                f"{target_name} was brutally murdered", is_strong=True
            )


def register(role_map):
    role_map.update(
        {PlayerRole.WOLF: RoleDetails(description, {GameStage.NIGHT: WolfAction})}
    )
