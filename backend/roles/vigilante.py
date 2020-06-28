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
from .utility_mixins import OncePerGame
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


class VigilanteAction(OncePerGame, GameAction):
    @classmethod
    def immediate(
        cls,
        game: "WurwolvesGame" = None,
        user_id=None,
        selected_id=None,
        stage_id=None,
        **kw,
    ):
        """Send the traditional message"""
        game.send_chat_message("BANG!!!", is_strong=True)

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
