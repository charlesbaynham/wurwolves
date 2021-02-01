"""
The Mayor role
"""
import logging
from typing import TYPE_CHECKING

from ..model import GameStage
from ..model import PlayerRole
from ..model import PlayerState
from ..resolver import ActionMixin
from ..resolver import GameAction
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .teams import Team
from .utility_mixins import NoTargetRequired
from .utility_mixins import TargetMustBeAlive
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame

general_description = """
You are on the side of the villagers and everyone knows who you are. While you are alive, there will be
no voting for lynching: you will make the decision unilaterally. You are allowed to take advice if you want,
but you don't have to listen to it.
"""

description = RoleDescription(
    display_name="You are the Mayor!",
    stages={
        GameStage.DAY: StageAction(
            text=f"""
{general_description}

When you're ready to decide who to lynch, click the button.
    """,
            button_text="Move to vote",
            select_person=False,
        ),
        GameStage.NIGHT: StageAction(
            text=f"""
{general_description}

It's night now so you have nothing to do. Let's hope your subjects are loyal!
    """
        ),
        GameStage.VOTING: StageAction(
            text=f"""
{general_description}

Select whoever you have decided needs to be lynched.
    """,
            button_text="Lynch",
        ),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class CancelledByMayor(ActionMixin):
    """
    This mixin should be added to actions which should be prevented if the Mayor
    is present, i.e. the villagers' Vote, the villaters' Move to vote and the narrator's Move to Vote
    """

    @classmethod
    def is_action_available(
        cls, game: "WurwolvesGame", stage: GameStage, stage_id: int, player_id: int
    ):
        """
        Check if a mayor is present and allow / disallow
        this action accordingly
        """
        mayor_is_present = game.is_role_present(PlayerRole.MAYOR, PlayerState.ALIVE)
        logging.debug(
            f"In mayor is_action_available, game.is_role_present(PlayerRole.MAYOR) = {mayor_is_present}"
        )

        out = not mayor_is_present

        if hasattr(super(), "is_action_available"):
            out = out and super().is_action_available(game, stage, stage_id, player_id)

        return out


class MayorMoveToVoteAction(GameAction, NoTargetRequired):
    """
    Move to vote

    The narrator is the only one who is allowed to vote, so the round will
    complete as soon as their action is submitted.
    """

    allowed_player_states = list(PlayerState)

    @classmethod
    def immediate(cls, game: "WurwolvesGame" = None, **kwargs):
        super().immediate(game=game, **kwargs)
        game.send_chat_message("The mayor started the lynching session")


class MayorVoteAction(TargetMustBeAlive, GameAction):
    def execute(self, game):
        msg = f"The mayor has executed {self.target.model.user.name}"
        logging.info(f"({game.game_id}) {msg}")
        game.send_chat_message(msg)
        game.vote_player(self.target.model.id)


def register(role_map):
    role_map.update(
        {
            PlayerRole.MAYOR: RoleDetails(
                role_description=description,
                actions={
                    GameStage.DAY: MayorMoveToVoteAction,
                    GameStage.VOTING: MayorVoteAction,
                },
            )
        }
    )
