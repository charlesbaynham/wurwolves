"""
The Villager role
"""
from ..model import PlayerRole
from .common import DEFAULT_ROLE, RoleDescription, RoleDetails


description = RoleDescription(
    display_name="Villager",
    stages={},
    team=RoleDescription.Team.VILLAGERS,
    fallback_role=DEFAULT_ROLE,
)


def register(role_map):
    role_map.update({PlayerRole.VILLAGER: RoleDetails(description, None)})
