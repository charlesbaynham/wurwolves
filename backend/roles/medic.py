"""
The Medic role

The Medic can save one person every night. 
"""
import logging

from ..model import GameStage, PlayerRole
from ..resolver import ActionMixin, GameAction
from .common import RoleDescription, RoleDetails, StageAction
from .villager import description as villager
from .teams import Team

description = RoleDescription(
    display_name="Medic",
    stages={
        GameStage.NIGHT: StageAction(
            text="""
You are a medic! You get to save one person each night. 

You win if all the wolves are eliminated. 
""",
            button_text="Select someone to save",
        ),
    },
    team=Team.VILLAGERS,
    secret_chat_enabled=True,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class AffectedByMedic(ActionMixin):
    """
    Creates attributes `target_saved_by_medic` and `originator_saved_by_medic`
    """

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
        # No action required: the medic's effect is to modify other actions
        # through the AffectedByMedic ActionMixin
        pass


def register(role_map):
    role_map.update(
        {PlayerRole.MEDIC: RoleDetails(description, {GameStage.NIGHT: MedicAction})}
    )
