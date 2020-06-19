"""
The Spectator role
"""
from ..model import PlayerRole, GameStage
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails, StageAction


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


def register(role_map):
    role_map.update({PlayerRole.SPECTATOR: RoleDetails(description, None)})
