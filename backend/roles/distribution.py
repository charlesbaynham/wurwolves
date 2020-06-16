import random
from ..model import PlayerRole


def assign_roles(num_players: int):
    # For now, just assign some random roles
    non_spectator_roles = list(PlayerRole)
    non_spectator_roles.remove(PlayerRole.SPECTATOR)

    return random.choices(non_spectator_roles, k=num_players)
