"""
The Vigilante role

Once per game, the vigilante may kill one person in the night
"""
from typing import TYPE_CHECKING

from ..model import GameStage, PlayerRole, PlayerState
from ..resolver import GameAction, RoundEndBehaviour
from .common import RoleDescription, RoleDetails, StageAction
from .medic import AffectedByMedic
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
            button_text="Select someone to shoot",
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


class VigilanteAction(OncePerGame, AffectedByMedic, GameAction):

    round_end_behaviour = RoundEndBehaviour.ONCE_OPTIONAL

    @classmethod
    def immediate(
        cls, game: "WurwolvesGame" = None, **kwargs,
    ):
        """Send the traditional message"""
        game.send_chat_message("BANG!!!", is_strong=True)

    def execute(self, game):
        target_name = self.target.model.user.name

        if not self.target_saved_by_medic:
            game.send_chat_message(f"{target_name} was shot", is_strong=True)
            game.kill_player(self.target.model.id, PlayerState.SHOT)


def register(role_map):
    role_map.update(
        {
            PlayerRole.VIGILANTE: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: VigilanteAction}
            )
        }
    )
