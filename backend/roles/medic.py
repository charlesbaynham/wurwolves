"""
The Medic role

The Medic can save one person every night. 
"""
from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..model import GameStage, PlayerRole
from ..resolver import ActionMixin, GameAction, ModifierType
from .common import RoleDescription, RoleDetails, StageAction
from .teams import Team
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


description = RoleDescription(
    display_name="Medic",
    stages={
        GameStage.NIGHT: StageAction(
            text="""
You are a medic! You get to save one person each night. 

It's night time now, so select one person to save then click the button to submit. 

You win if all the wolves are eliminated. 
""",
            button_text="Select someone to save",
        ),
        GameStage.DAY: StageAction(
            text="""
You are a medic! You get to save one person each night. 
        """
        ),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class AffectedByMedic(ActionMixin):
    """
    Creates attributes `target_saved_by_medic` and `originator_saved_by_medic`
    """

    def __init_subclass__(cls):
        cls.bind_as_modifier(
            AffectedByMedic.__orig_saved,
            AffectedByMedic,
            MedicAction,
            ModifierType.ORIGINATING_FROM_TARGET,
        )
        cls.bind_as_modifier(
            AffectedByMedic.__target_saved,
            AffectedByMedic,
            MedicAction,
            ModifierType.TARGETTING_TARGET,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_saved_by_medic = False
        self.originator_saved_by_medic = False

    def __orig_saved(self, action: "MedicAction"):
        if not action.prevented:
            self.originator_saved_by_medic = True

    def __target_saved(self, action: "MedicAction"):
        if not action.prevented:
            self.target_saved_by_medic = True


class MedicAction(GameAction):
    @classmethod
    def immediate(
        cls,
        game: "WurwolvesGame" = None,
        user_id=None,
        selected_id=None,
        stage_id=None,
        **kw,
    ):
        """
        Decide if this medic action is valid. If not, raise an exception so that the user is informed
        """
        my_player_id = game.get_player_id(user_id)
        selected_player_id = game.get_player_id(selected_id)

        medic_actions = game.get_actions_model(
            player_id=my_player_id, stage=GameStage.NIGHT
        )

        if not medic_actions:
            return

        # Sort medic actions by stage_id to get the most recent
        sorted_actions = sorted(medic_actions, key=lambda a: a.stage_id, reverse=True)

        if sorted_actions[0].selected_player_id == selected_player_id:
            raise HTTPException(403, "You can't save the same person twice in a row")


def register(role_map):
    role_map.update(
        {
            PlayerRole.MEDIC: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: MedicAction}
            )
        }
    )
