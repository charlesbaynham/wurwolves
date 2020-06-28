"""
The Spectator role
"""
import logging
from typing import TYPE_CHECKING

from ..model import GameStage, PlayerRole, PlayerState
from ..resolver import NoTargetRequired, RoundEndBehaviour
from .common import GameAction, RoleDescription, RoleDetails, StageAction
from .teams import Team

if TYPE_CHECKING:
    from ..game import WurwolvesGame


game_desc = StageAction(
    text={
        "default": "You're not playing. Guess you were late.",
        PlayerState.WOLFED: "You were killed by a werewolf!",
        PlayerState.LYNCHED: "You got lynched! Ouch.",
    },
    button_text="Become narrator",
    select_person=False,
)


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
        GameStage.DAY: game_desc,
        GameStage.NIGHT: game_desc,
        GameStage.VOTING: game_desc,
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


class VoteStartNewGame(GameAction, NoTargetRequired):
    """
    Vote to start a new game. 

    When all eligable players have voted, the finalizer will be called which will advance the game. This
    GameAction doesn't therefore have to do it. 
    """

    allowed_player_states = list(PlayerState)

    @classmethod
    def immediate(cls, game=None, user_id=None, **kwargs):
        msg = f"{game.get_user_name(user_id)} wants to start a new game"
        logging.info(f"({game.game_id}) {msg}")
        game.send_chat_message(msg)

    def execute(self, game):
        pass


def register(role_map):
    from .narrator import CancelledByNarrator

    # Define this here to avoid circular imports with narrator
    class BecomeNarratorAction(CancelledByNarrator, GameAction):
        """
        Allow spectators to become the narrator if they want. 

        CancelledByNarrator so that only one person can narrate. 
        """

        allowed_player_states = list(PlayerState)

        round_end_behaviour = RoundEndBehaviour.ONCE_OPTIONAL

        @classmethod
        def immediate(cls, game: "WurwolvesGame" = None, user_id=None, **kw):
            game.set_player_role(game.get_player_id(user_id), PlayerRole.NARRATOR)

            # Return false to abort the storage of this action, otherwise it'll count
            # as this player's action for the round
            return False

    role_map.update(
        {
            PlayerRole.SPECTATOR: RoleDetails(
                description,
                {
                    GameStage.LOBBY: VoteStartNewGame,
                    GameStage.ENDED: VoteStartNewGame,
                    GameStage.DAY: BecomeNarratorAction,
                    GameStage.NIGHT: BecomeNarratorAction,
                    GameStage.VOTING: BecomeNarratorAction,
                },
            )
        }
    )
