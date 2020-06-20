"""
The Villager role
"""
import logging

from ..model import GameStage, PlayerRole
from ..resolver import GameAction
from .common import RoleDescription, RoleDetails, StageAction

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
    fallback_role=None,
)


class MoveToVoteAction(GameAction):
    def execute(self, game):
        msg = f"{self.originator.user.name} voted for {self.target.model.user.name}"
        logging.warning(msg)
        game.send_chat_message(msg)


def register(role_map):
    role_map.update({PlayerRole.VILLAGER: RoleDetails(description)})
