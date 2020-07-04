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
RANDOMISED_ROLES = {
    PlayerRole.JESTER: 10,
    PlayerRole.VIGILANTE: 10,
    PlayerRole.MAYOR: 10,
    PlayerRole.MILLER: 10,
    PlayerRole.ACOLYTE: 7,
    PlayerRole.PRIEST: 10,
    PlayerRole.PROSTITUTE: 10,
}

all_distributed_roles = (
    guaranteed_roles
    + list(RANDOMISED_ROLES.keys())
    + [PlayerRole.WOLF, PlayerRole.VILLAGER, PlayerRole.NARRATOR, PlayerRole.SPECTATOR]
)
for role in list(PlayerRole):
    if role not in all_distributed_roles:
        raise TypeError(f"Role {role} is not available to be assigned")

DUAL_ROLES = []

# Average probability that a player is a villager
# This cannot be satisfied for very small games (because all the guaranteed roles
# must be handed out) or for very large games (because there aren't enough optional
# roles to go around) but the algorithm will do its best
PROB_VILLAGER = 0.20


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
        return math.ceil(num_players / 5)


def assign_roles(
    num_players: int, probability_of_villager=PROB_VILLAGER
) -> List[PlayerRole]:
    """
    Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """

    if num_players < len(guaranteed_roles) + 1:
        return None

    # Decide the number of villagers
    num_villagers = sum(
        random.random() < probability_of_villager for _ in range(num_players)
    )
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
    remaining_roles_and_weights = RANDOMISED_ROLES.copy()

    while len(roles) < num_players:
        if not remaining_roles_and_weights:
            # Raised if there are no roles remaining
            roles.append(PlayerRole.VILLAGER)
        else:
            remaining_roles, remaining_weights = zip(
                *remaining_roles_and_weights.items()
            )
            chosen_role = random.choices(remaining_roles, remaining_weights)[0]

            if chosen_role in DUAL_ROLES:
                remaining_slots = len(roles) - num_players

                if remaining_slots < 2:
                    # If we can't fit two more players, remove this role from the options and try again
                    pass
                else:
                    roles += [chosen_role] * 2
            else:
                roles.append(chosen_role)

            del remaining_roles_and_weights[chosen_role]

    # Shuffle the list and return
    random.shuffle(roles)

    return roles
