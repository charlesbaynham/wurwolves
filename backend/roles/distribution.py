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
probability_of_villager = 0.25


def num_wolves(num_players: int):
    return 1


def assign_roles(num_players: int) -> List[PlayerRole]:
    """
    Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """

    if num_players < len(guaranteed_roles)+1:
        return None

    # Fill in the guaranteed roles and the wolves
    roles = [PlayerRole.WOLF] * num_wolves(num_players)
    roles += guaranteed_roles

    # Stop if there are no places left
    if len(roles) == num_players:
        random.shuffle(roles)
        return roles

    # For the rest, calculate the village vs option probability given
    # the chosen probability_of_any_role and the roles already handed out
    prob_villager_in_rest = probability_of_villager / (1 - len(roles)/num_players)

    # Prepare a list of optional roles and weightings
    opt_roles, opt_weighs = zip(*randomised_roles.items())

    # For each remaining player, pick either villager or an optional role
    for _ in range(num_players-len(roles)):
        if (random.random() < prob_villager_in_rest
                or not opt_roles):
            roles += [PlayerRole.VILLAGER]
        else:
            # Not a villager, so choose a random optional role
            rand_index = random.choices(range(len(opt_roles)), weights=opt_weighs)[0]
            roles += [opt_roles[rand_index]]
            del opt_roles[rand_index]
            del opt_weighs[rand_index]

    # Shuffle the list and return
    random.shuffle(roles)

    return roles


def weighted_sample_without_replacement(population, weights, k=1):
    """
    Random sample without replacement but with weights

    From https://stackoverflow.com/questions/43549515/weighted-random-sample-without-replacement-in-python
    """
    weights = list(weights)
    positions = range(len(population))
    indices = []
    while True:
        needed = k - len(indices)
        if not needed:
            break
        for i in random.choices(positions, weights, k=needed):
            if weights[i]:
                weights[i] = 0.0
                indices.append(i)
    return [population[i] for i in indices]
