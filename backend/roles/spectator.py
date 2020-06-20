"""
The Spectator role
"""
import logging

from ..model import GameStage, PlayerRole
from .common import DEFAULT_ROLE, GameAction, RoleDescription, RoleDetails, StageAction

description = RoleDescription(
    display_name="Spectator",
    stages={
        GameStage.DAY: StageAction(text="You're not playing. Guess you were late."),
        GameStage.NIGHT: StageAction(text="You're not playing. Guess you were late."),
        GameStage.VOTING: StageAction(text="You're not playing. Guess you were late."),
    },
    team=RoleDescription.Team.SPECTATORS,
    fallback_role=DEFAULT_ROLE,
)


class StartGameAction(GameAction):
    def execute(self, game):
        logging.warning("started game: {}".format(self))

    @classmethod
    def immediate(cls, game):
        logging.warning("Immediate fire from spectator")


def register(role_map):
    role_map.update(
        {
            PlayerRole.SPECTATOR: RoleDetails(
                description, {GameStage.LOBBY: StartGameAction}
            )
        }
    )
