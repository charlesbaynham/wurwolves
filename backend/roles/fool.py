"""
The Fool role

The fool thinks that they are the seer! But they just get random answers instead.
"""
import logging
import random

from ..model import GameStage
from ..model import PlayerRole
from ..resolver import GameAction
from .common import RoleDescription
from .common import RoleDetails
from .common import StageAction
from .miller import ConfusedByMiller
from .seer import description as seer_description
from .seer import SeerAction
from .teams import Team
from .utility_mixins import TargetMustBeAlive
from .villager import description as villager
from .wolf import AffectedByWolves

if False:  # for typing
    from ..game import WurwolvesGame

description = RoleDescription(
    display_name="You are the Fool!",
    stages={
        # No stages are relevant here, since this RoleDescription
        # is only used in ENDED, where we don't want custom text.
        # I'll pass the Seer's controls through anyway though, to stop
        # the error validation in registration.py getting upset
        GameStage.NIGHT: seer_description.stages[GameStage.NIGHT]
    },
    team=Team.VILLAGERS,
    fallback_role=PlayerRole.VILLAGER,
    fallback_role_description=villager,
    masked_role_in_stages={
        GameStage.DAY: PlayerRole.SEER,
        GameStage.NIGHT: PlayerRole.SEER,
        GameStage.VOTING: PlayerRole.SEER,
    },
)


class FoolAction(ConfusedByMiller, AffectedByWolves, TargetMustBeAlive, GameAction):
    def execute(self, game: "WurwolvesGame"):
        from .registration import get_role_team

        fool_name = self.originator.model.user.name
        target_name = self.target.model.user.name

        target_is_wolf = bool(random.randint(0, 1))

        logging.info(f"Foor: {fool_name} checks {target_name}")

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
        elif target_is_wolf:
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
            PlayerRole.FOOL: RoleDetails(
                role_description=description, actions={GameStage.NIGHT: FoolAction}
            )
        }
    )
