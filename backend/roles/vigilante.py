"""
The Vigilante role

Once per game, the vigilante may kill one person in the night
"""
from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..model import GameStage, PlayerRole
from ..resolver import ActionMixin, GameAction
from .common import RoleDescription, RoleDetails, StageAction
from .teams import Team
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


description = RoleDescription(
    display_name="Vigilante",
    stages={
        GameStage.NIGHT: StageAction(
            text="""
You are a vigilante! Once per game, you can shoot someone in the night. 

It's night time now, so if you want to act, select someone to shoot. 

You win if all the wolves are eliminated. 
""",
            button_text="Select someone to save",
        ),
        GameStage.DAY: StageAction(
            text="""
You are a vigilante! Once per game, you can shoot someone in the night. 
        """
        ),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class VigilanteAction(GameAction):
    @classmethod
    def is_action_available(
        cls, game: "WurwolvesGame", stage: GameStage, stage_id: int, player_id: int
    ):
        """
        Disallow the action if it's already been done this game
        """
        previous_actions = game.get_actions_model(
            player_id=player_id, stage=GameStage.NIGHT
        )

        return not bool(previous_actions)

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
        Decide if this vigilante action is valid. If not, raise an exception so that the user is informed
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

    def execute(self, game):
        # No action required: the medic's effect is to modify other actions
        # through the AffectedByMedic ActionMixin
        pass


def register(role_map):
    role_map.update(
        {
            PlayerRole.VIGILANTE: RoleDetails(
                description, {GameStage.NIGHT: VigilanteAction}
            )
        }
    )
