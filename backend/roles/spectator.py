'''
The Spectator role
'''
from ..model import PlayerRole
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Spectator",
    night_action=False,
    day_text="You're not playing. Guess you were late.",
    night_text="You're not playing. Guess you were late.",
    vote_text="You're not playing. Guess you were late.",
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({
        PlayerRole.SPECTATOR: RoleDetails(description, None)
    })
