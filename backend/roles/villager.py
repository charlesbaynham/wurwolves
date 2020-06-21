"""
The Villager role
"""
import logging
from typing import TYPE_CHECKING

from ..model import GameStage, PlayerRole
from ..resolver import GameAction, NoTargetRequired, TargetRequired
from .common import RoleDescription, RoleDetails, StageAction

if TYPE_CHECKING:
    from ..game import WurwolvesGame

description = RoleDescription(
    display_name="Villager",
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
You have nothing to do at night. Relax...
    """
        ),
        GameStage.VOTING: StageAction(
            text="""
Vote for someone to lynch! Whoever gets the most votes will be killed.

Click someone's icon and click the button. 
    """,
            button_text="Vote for someone to lynch...",
        ),
        GameStage.LOBBY: StageAction(text="",),
    },
    team=RoleDescription.Team.VILLAGERS,
)


class MoveToVoteAction(GameAction, NoTargetRequired):
    """
    Move to vote

    This just sends a message: the round completes when all players have moved to vote
    """

    def execute(self, game):
        pass

    @classmethod
    def immediate(cls, game: "WurwolvesGame" = None, user_id=None, **kwargs):
        msg = f"{game.get_user_name(user_id)} moved to vote"
        game.send_chat_message(msg)


class VoteAction(GameAction, TargetRequired):
    def execute(self, game):
        msg = f"({game.game_id}) {self.originator.model.user.name} voted for {self.target.model.user.name}"
        logging.info(msg)
        game.send_chat_message(msg)
        game.vote_player(self.target.model.id)


def register(role_map):
    role_map.update(
        {
            PlayerRole.VILLAGER: RoleDetails(
                description,
                {GameStage.DAY: MoveToVoteAction, GameStage.VOTING: VoteAction},
            )
        }
    )
