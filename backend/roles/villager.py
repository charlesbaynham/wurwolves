"""
The Villager role
"""
import logging
from typing import TYPE_CHECKING

from ..model import GameStage
from ..model import PlayerRole
from ..resolver import GameAction
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .spectator import BackToLobby
from .spectator import VoteStartNewGame
from .teams import Team
from .utility_mixins import NoTargetRequired
from .utility_mixins import TargetMustBeAlive

if TYPE_CHECKING:
    from ..game import WurwolvesGame

description = RoleDescription(
    display_name="You are a Villager",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a villager. You have no special powers. Try not to get eaten!

You win if all the wolves are eliminated.
    """,
            button_text="Move to vote",
            select_person=False,
        ),
        GameStage.NIGHT: StageAction(
            text="""
You are a villager. You have no special powers. Try not to get eaten!

You have nothing to do at night. Try to relax...
    """
        ),
        GameStage.VOTING: StageAction(
            text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon to select them.
    """,
            button_text="Vote for someone to lynch...",
        ),
        GameStage.LOBBY: StageAction(
            text="",
        ),
        GameStage.ENDED: StageAction(
            text="The game has ended!",
            button_text="Back to lobby",
            select_person=False,
        ),
    },
    team=Team.VILLAGERS,
)


def register(role_map):
    from .mayor import CancelledByMayor
    from .narrator import CancelledByNarrator

    class MoveToVoteAction(
        CancelledByMayor, CancelledByNarrator, NoTargetRequired, GameAction
    ):
        """
        Move to vote

        This just sends a message: the round completes when all players have moved to vote
        """

    class VoteAction(CancelledByMayor, TargetMustBeAlive, GameAction):
        def execute(self, game: "WurwolvesGame"):
            msg = f"{self.originator.model.user.name} voted for {self.target.model.user.name}"
            logging.info(f"({game.game_id}) {msg}")
            game.send_chat_message(msg)
            game.vote_player(self.target.model.id)

    role_map.update(
        {
            PlayerRole.VILLAGER: RoleDetails(
                role_description=description,
                actions={
                    GameStage.DAY: MoveToVoteAction,
                    GameStage.VOTING: VoteAction,
                    GameStage.ENDED: BackToLobby,
                },
            )
        }
    )
