"""
The Villager role
"""
from ..model import PlayerRole
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Villager",
    night_action=False,
    day_text=None,
    night_text=None,
    vote_text=None,
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({PlayerRole.VILLAGER: RoleDetails(description, None)})
