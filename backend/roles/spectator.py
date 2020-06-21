"""
The Spectator role
"""
import logging

from ..model import GameStage, PlayerRole, PlayerState
from ..resolver import NoTargetRequired
from .common import GameAction, RoleDescription, RoleDetails, StageAction
from .teams import Team

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
        GameStage.ENDED: StageAction(
            text="""
The game has ended!

Click the button to play again. The game will start once all spectators have voted to start. """,
            button_text="Vote to restart",
            select_person=False,
        ),
    },
    team=Team.SPECTATORS,
)


class StartGameAction(GameAction):

    allowed_player_states = list(PlayerState)

    def execute(self, game):
        logging.warning("Spectator action: {}".format((self, game)))

    @classmethod
    def immediate(cls, game=None, user_id=None, **kwargs):
        msg = f"{game.get_user_name(user_id)} wants to start the game"
        logging.info(f"({game.game_id}) {msg}")
        game.send_chat_message(msg)
        game.vote_start()


class VoteStartNewGame(GameAction, NoTargetRequired):
    allowed_player_states = list(PlayerState)

    @classmethod
    def immediate(cls, game=None, user_id=None, **kwargs):
        msg = f"{game.get_user_name(user_id)} wants to start a new game"
        logging.info(f"({game.game_id}) {msg}")
        game.send_chat_message(msg)
        game.vote_start()

    def execute(self, game):
        pass


def register(role_map):
    role_map.update(
        {
            PlayerRole.SPECTATOR: RoleDetails(
                description,
                {GameStage.LOBBY: StartGameAction, GameStage.ENDED: VoteStartNewGame},
            )
        }
    )
