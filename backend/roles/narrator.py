"""
The Narrator role
"""
import logging
from typing import TYPE_CHECKING

from ..model import GameStage, PlayerRole, PlayerState
from ..resolver import ActionMixin, GameAction, NoTargetRequired
from .common import RoleDescription, RoleDetails, StageAction
from .spectator import description as spectator_description
from .teams import Team

if TYPE_CHECKING:
    from ..game import WurwolvesGame

general_description = """
You are the narrator. You are not playing the game and cannot win, but you 
are in charge of keeping the game on track. 

You control when the vote begins and you should announce the deaths that happen
in the night (although they'll still get written in the chat). If you're feeling inventive, add a backstory. 

Try to keep the game moving! It's up to you to ensure that the conversation doesn't get bogged down. 
"""

description = RoleDescription(
    display_name="Narrator",
    stages={
        GameStage.DAY: StageAction(
            text=f"""
{general_description}

When you're ready to start the voting for the day, click the button. 
    """,
            button_text="Move to vote",
            select_person=False,
        ),
        GameStage.NIGHT: StageAction(
            text=f"""
{general_description}

You don't have anything to do at night. Watch the chat log to see what people are up to.
If someone isn't doing their action you can remind them, but be careful not to
reveal their identity! When the day breaks, you can announce the results. 
    """
        ),
        GameStage.VOTING: StageAction(
            text=f"""
{general_description}

The players should be voting! The game will automatically progress once they're finished. 
    """,
        ),
        GameStage.LOBBY: StageAction(text=""),
        GameStage.ENDED: StageAction(
            text="The game has ended!",
            button_text="Vote to restart",
            select_person=False,
        ),
    },
    team=Team.NARRATOR,
    fallback_role=PlayerRole.SPECTATOR,
    fallback_role_description=spectator_description,
)


class CancelledByNarrator(ActionMixin):
    """
    This mixin should be added to actions which should be prevented if the Narrator
    is present, i.e. the villagers' Move to Vote
    """

    @classmethod
    def is_action_available(
        cls, game: "WurwolvesGame", stage: GameStage, stage_id: int, player_id: int
    ):
        """
        Check if a narrator is present and allow / disallow
        the villagers from voting accordingly
        """
        narrator_is_present = game.is_role_present(PlayerRole.NARRATOR)
        logging.info(
            f"In narrator is_action_available, game.is_role_present(PlayerRole.NARRATOR) = {narrator_is_present}"
        )
        return not narrator_is_present


class NarratorMoveToVoteAction(GameAction, NoTargetRequired):
    """
    Move to vote

    The narrator is the only one who is allowed to vote, so the round will
    complete as soon as their action is submitted. 
    """

    allowed_player_states = list(PlayerState)

    def execute(self, game):
        pass

    @classmethod
    def immediate(cls, game: "WurwolvesGame" = None, **kwargs):
        game.send_chat_message("The narrator started the voting session")


def register(role_map):
    role_map.update(
        {
            PlayerRole.NARRATOR: RoleDetails(
                description, {GameStage.DAY: NarratorMoveToVoteAction},
            )
        }
    )
