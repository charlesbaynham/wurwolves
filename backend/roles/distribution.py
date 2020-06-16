import random
from typing import List

from ..model import PlayerRole

guaranteed_roles = [
    PlayerRole.SEER,
    PlayerRole.MEDIC,
]

randomised_roles = {
    PlayerRole.JESTER: 1
}

role_villager = PlayerRole.VILLAGER
role_wolf = PlayerRole.WOLF

# Average ratio of villagers to non-guaranteed roles
# E.g. "2" means twice as many villages as optional roles
average_villager_ratio = 0.5


def num_wolves(num_players: int):
    return 1


def assign_roles(num_players: int) -> List[PlayerRole]:
    """Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """

    if num_players < len(guaranteed_roles)+1:
        return None

    roles = [PlayerRole.WOLF] * num_wolves(num_players)
    roles += guaranteed_roles

    villager_weighting = average_villager_ratio * sum(randomised_roles.values())

    optional_roles, optional_weightings = zip(*randomised_roles.items())
    roles += random.choices(
        population=list(optional_roles) + [PlayerRole.VILLAGER],
        weights=list(optional_weightings) + [villager_weighting],
        k=num_players-len(roles)
    )

    return roles
