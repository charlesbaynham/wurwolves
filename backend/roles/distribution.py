import random
from typing import List

from ..model import PlayerRole


role_probabilities = {
    PlayerRole.SEER: 1,
    PlayerRole.MEDIC: 1,
}

role_default = PlayerRole.VILLAGER
role_wolf = PlayerRole.WOLF


def num_wolves(num_players: int):
    return 1


def assign_roles(num_players: int) -> List[PlayerRole]:
    """Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """
    
    roles = [PlayerRole.WOLF] * num_wolves(num_players)
    

    return random.choices(non_spectator_roles, k=num_players)
