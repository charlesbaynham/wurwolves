import math
import random
from typing import List

from ..model import PlayerRole

guaranteed_roles = [
    PlayerRole.SEER,
    PlayerRole.MEDIC,
]

# Roles with weightings
# Weightings only have meaning relative to each other
randomised_roles = {
    PlayerRole.JESTER: 20
}

# Average probability that a player is a villager
# This cannot be satisfied for very small games (because all the guaranteed roles
# must be handed out) or for very large games (because there aren't enough optional
# roles to go around) but the algorithm will do its best
PROB_VILLAGER = 0.25


def num_wolves(num_players: int):
    lookup = {
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 2,
        8: 2,
        9: 2,
        10: 3,
        11: 3,
        12: 3,
        13: 3,
        14: 3,
        15: 3,
    }

    try:
        return lookup[num_players]
    except KeyError:
        return math.ceil(num_players/5)


def assign_roles(num_players: int, probability_of_villager=PROB_VILLAGER) -> List[PlayerRole]:
    """
    Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """

    if num_players < len(guaranteed_roles)+1:
        return None

    # Decide the number of villagers
    num_villagers = sum(random.random() < probability_of_villager for _ in range(num_players))
    max_num_villagers = num_players - num_wolves(num_players) - len(guaranteed_roles)
    if num_villagers > max_num_villagers:
        num_villagers = max_num_villagers

    # Fill in the guaranteed roles and the wolves
    roles = [PlayerRole.WOLF] * num_wolves(num_players)
    roles += guaranteed_roles

    # Fill in the villagers
    roles += [PlayerRole.VILLAGER] * num_villagers

    # For the rest, pick from the optional roles
    # Prepare a list of optional roles and weightings
    opt_roles, opt_weighs = zip(*randomised_roles.items())

    roles += weighted_sample_without_replacement(
        opt_roles, opt_weighs, num_players - len(roles), fallback=PlayerRole.VILLAGER
    )

    # Shuffle the list and return
    random.shuffle(roles)

    return roles


def weighted_sample_without_replacement(population, weights, k=1, fallback=None):
    """
    Random sample without replacement but with weights

    If we run out of the population, fill the rest of the sample with fallback

    From https://stackoverflow.com/questions/43549515/weighted-random-sample-without-replacement-in-python
    """
    if k < 0 or not isinstance(k, int):
        raise ValueError
    weights = list(weights)
    positions = range(len(population))
    indices = []
    while True:
        needed = k - len(indices)
        if not needed:
            break
        for i in random.choices(positions, weights, k=needed):
            if not any(weights):
                indices.append(None)
            if weights[i]:
                weights[i] = 0.0
                indices.append(i)
    return [fallback if i is None else population[i]
            for i in indices]
