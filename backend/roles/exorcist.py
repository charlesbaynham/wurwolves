"""
The Exorcist role

Once per game, the exorcist may attempt to drive out one person in the night. If
they are a wolf, they are killed. If they are not, the exorcist is killed.
"""
from typing import TYPE_CHECKING
from uuid import UUID

from ..model import GameStage
from ..model import PlayerRole
from ..model import PlayerState
from ..resolver import GameAction
from ..resolver import RoundEndBehaviour
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .medic import AffectedByMedic
from .teams import Team
from .utility_mixins import OncePerGame
from .utility_mixins import TargetMustBeAlive
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


description = RoleDescription(
    display_name="You are an Exorcist",
    stages={
        GameStage.NIGHT: StageAction(
            text="""
You are an exorcist! Once per game, you can attempt to exorcise a wolf.

If you choose a wolf, you will kill them. But, if you choose a non-wolf, YOU
will die. So choose carefully.

It's night time now, so you can act if you want to. If not, just wait.

You win if all the wolves are eliminated.
""",
            button_text="Select someone to exorcise",
        ),
        GameStage.DAY: StageAction(
            text="""
You are a exorcist! Once per game, you can attempt to exorcise a wolf.

If you choose a wolf, you will kill them. But, if you choose a non-wolf, YOU
will die. So choose carefully.

You win if all the wolves are eliminated.
        """
        ),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class ExorcistAction(OncePerGame, TargetMustBeAlive, GameAction):

    round_end_behaviour = RoundEndBehaviour.ONCE_OPTIONAL

    @classmethod
    def immediate(
        cls,
        game: "WurwolvesGame" = None,
        user_id: UUID = None,
        **kwargs,
    ):
        super().immediate(game=game, **kwargs)
        game.send_chat_message("You chose...", is_strong=True, user_list=[user_id])

    def execute(self, game):
        from .registration import get_role_team

        if self.prevented:
            game.send_chat_message(
                f"...to do something else tonight",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
            return

        if get_role_team(self.target.model.role) == Team.WOLVES:
            game.send_chat_message(
                f"...wisely!",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
            death_player = self.target.model
        else:
            game.send_chat_message(
                f"...poorly!",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
            death_player = self.originator.model

        game.send_chat_message(
            f"{death_player.user.name} was brutally murdered", is_strong=True
        )
        game.kill_player(death_player.id, PlayerState.WOLFED)


def register(role_map):
    role_map.update(
        {
            PlayerRole.EXORCIST: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: ExorcistAction}
            )
        }
    )
