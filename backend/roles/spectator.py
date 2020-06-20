"""
The Spectator role
"""
import logging

from ..model import GameStage, PlayerRole
from .common import GameAction, RoleDescription, RoleDetails, StageAction

description = RoleDescription(
    display_name="Spectator",
    stages={
        GameStage.LOBBY: StageAction(
            text="""
Welcome to Wurwolves! 
The game hasn't started yet: you'll need at least 5 players for the game to be playable,
but it's more fun with 7 or more. Once everyone has joined, press the \"Start game\" button. 

To invite more people, just send them the link to this page. 

This website is designed for playing with people you already know:
it handles the gameplay but you'll also need to communicate so you
can argue and discuss what happens. If you're not in the same room,
you should probably start a video call. 
    """,
            button_text="Start game",
            select_person=False,
        ),
        GameStage.DAY: StageAction(text="You're not playing. Guess you were late."),
        GameStage.NIGHT: StageAction(text="You're not playing. Guess you were late."),
        GameStage.VOTING: StageAction(text="You're not playing. Guess you were late."),
    },
    team=RoleDescription.Team.SPECTATORS,
)


class StartGameAction(GameAction):
    def execute(self, game):
        logging.warning("Spectator action: {}".format((self, game)))

    @classmethod
    def immediate(cls, game):
        logging.warning("Immediate fire from spectator: {}".format((cls, game)))
        game.vote_start()


def register(role_map):
    role_map.update(
        {
            PlayerRole.SPECTATOR: RoleDetails(
                description, {GameStage.LOBBY: StartGameAction}
            )
        }
    )
