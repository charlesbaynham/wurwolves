"""
The Priest role

Once per game, the priest may check the role of a dead player
"""
from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..model import DEAD_STATES
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
from .villager import description as villager

if TYPE_CHECKING:
    from ..game import WurwolvesGame


general_desc = """
Oh holy priest, you receive the confessions of the flock in this village. Of course,
the Seal of the Confessional is inviolable, but occasionally things slip your tounge.

Once per game you may check a dead player to learn what their role was.
You win if all the wolves are eliminated.

"""

description = RoleDescription(
    display_name="Priest",
    stages={
        GameStage.NIGHT: StageAction(
            text=f"""
{general_desc}

It's night now, so you can act if you want.
""",
            button_text="Select someone to remember about",
        ),
        GameStage.DAY: StageAction(text=general_desc),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class PriestCheckRole(OncePerGame, GameAction):

    round_end_behaviour = RoundEndBehaviour.ONCE_OPTIONAL

    @classmethod
    def immediate(
        cls,
        game: "WurwolvesGame" = None,
        selected_id=None,
        **kwargs,
    ):
        """Confirm that the selected player is dead"""
        super().immediate(game=game, selected_id=selected_id, **kwargs)
        if game.get_player_model(selected_id).state not in DEAD_STATES:
            raise HTTPException(403, "Your target must have died")

    def execute(self, game):
        originator_id = self.originator.model.id
        target_name = self.target.model.user.name
        role = self.target.model.previous_role

        if self.prevented:
            game.send_chat_message(
                (
                    f"You think hard about {target_name} but you just can't remember. "
                    "Maybe something is distracting you..."
                ),
                is_strong=True,
                player_list=[originator_id],
            )
        else:
            if not role:
                raise RuntimeError(
                    f"previous_role not specified for player {target_name}"
                )

            game.send_chat_message(
                f"You remember that {target_name} was a {role.value}",
                is_strong=True,
                player_list=[originator_id],
            )


def register(role_map):
    role_map.update(
        {
            PlayerRole.PRIEST: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: PriestCheckRole}
            )
        }
    )
