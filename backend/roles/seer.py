"""
The Seer role
"""
import logging

from ..model import GameStage
from ..model import PlayerRole
from ..resolver import GameAction
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .miller import ConfusedByMiller
from .teams import Team
from .utility_mixins import TargetMustBeAlive
from .villager import description as villager
from .wolf import AffectedByWolves

if False:  # for typing
    from ..game import WurwolvesGame

description = RoleDescription(
    display_name="You are the Seer",
    stages={
        GameStage.DAY: StageAction(
            text="""
You are a Seer! You get to check the identity of one person each night.

You win if all the wolves are eliminated.
    """
        ),
        GameStage.NIGHT: StageAction(
            text="""
You are a Seer! You get to check the identity of one person each night.

Choose whom to check: at the end of the night, you'll find out if they are a wolf.
    """,
            button_text="Select someone to check",
        ),
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
)


class SeerAction(ConfusedByMiller, AffectedByWolves, TargetMustBeAlive, GameAction):
    def execute(self, game: "WurwolvesGame"):
        from .registration import get_role_team

        seer_name = self.originator.model.user.name
        target_name = self.target.model.user.name
        target_is_wolf = get_role_team(self.target.model.role) == Team.WOLVES

        logging.info(f"Seer: {seer_name} checks {target_name}")

        if self.prevented:
            game.send_chat_message(
                f"You tried to check {target_name} but you couldn't concentrate",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
        elif self.originator_attacked_by_wolf:
            game.send_chat_message(
                f"You checked {target_name} but were rudely interrupted",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
        elif target_is_wolf or self.target_is_miller:
            game.send_chat_message(
                f"You checked {target_name}... they are a wolf!",
                is_strong=True,
                player_list=[self.originator.model.id],
            )
        else:
            game.send_chat_message(
                f"You checked {target_name}... they are not a wolf",
                is_strong=True,
                player_list=[self.originator.model.id],
            )


def register(role_map):
    role_map.update(
        {
            PlayerRole.SEER: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: SeerAction}
            )
        }
    )
