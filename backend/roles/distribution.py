import math
import random
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pydantic

from ..model import DistributionSettings
from ..model import PlayerRole

guaranteed_roles = [
    PlayerRole.SEER,
    PlayerRole.MEDIC,
]

# Roles with weightings
# Weightings only have meaning relative to each other
RANDOMISED_ROLES = {
    PlayerRole.JESTER: 20,
    PlayerRole.VIGILANTE: 10,
    PlayerRole.MAYOR: 10,
    PlayerRole.MILLER: 10,
    PlayerRole.ACOLYTE: 5,
    PlayerRole.PRIEST: 10,
    PlayerRole.PROSTITUTE: 10,
    PlayerRole.MASON: 7,
    PlayerRole.EXORCIST: 10,
    PlayerRole.FOOL: 10,
}

DUAL_ROLES = [PlayerRole.MASON]

all_distributed_roles = (
    guaranteed_roles
    + list(RANDOMISED_ROLES.keys())
    + [PlayerRole.WOLF, PlayerRole.VILLAGER, PlayerRole.NARRATOR, PlayerRole.SPECTATOR]
)
for role in list(PlayerRole):
    if role not in all_distributed_roles:
        raise TypeError(f"Role {role} is not available to be assigned")

# Average probability that a player is a villager
# This cannot be satisfied for very small games (because all the guaranteed roles
# must be handed out) or for very large games (because there aren't enough optional
# roles to go around) but the algorithm will do its best
PROB_VILLAGER = 0.1


def _default_num_wolves(num_players: int):
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
    num_players: int, settings: Union[None, DistributionSettings]
) -> List[PlayerRole]:
    """
    Return a randomised list of roles for this game, or None if not enough players have joined

    Args:
        num_players (int): Number of roles to assign

    Returns:
        List[PlayerRole]: A num_players long list of PlayerRoles in a random order
    """

    if settings is None:
        settings = DistributionSettings()

    if not isinstance(settings, DistributionSettings):
        raise TypeError(
            "Settings must be None or a DistributionSettings object. Got {}".format(
                type(settings)
            )
        )

    probability_of_villager = (
        settings.probability_of_villager
        if settings.probability_of_villager is not None
        else PROB_VILLAGER
    )

    if isinstance(settings.number_of_wolves, int):
        num_wolves = settings.number_of_wolves
    elif settings.number_of_wolves is None:
        num_wolves = _default_num_wolves(num_players)
    else:
        raise TypeError(
            "settings.number_of_wolves is a %s", type(settings.number_of_wolves)
        )

    role_weights = (
        settings.role_weights.copy()
        if settings.role_weights is not None
        else RANDOMISED_ROLES.copy()
    )
    # Filter out anything with zero weighting
    role_weights = {r: w for r, w in role_weights.items() if w > 0}

    if num_players < len(guaranteed_roles) + num_wolves:
        return None

    # Decide the number of villagers
    num_villagers = sum(
        random.random() < probability_of_villager for _ in range(num_players)
    )
    max_num_villagers = num_players - num_wolves - len(guaranteed_roles)
    if num_villagers > max_num_villagers:
        num_villagers = max_num_villagers

    # Fill in the guaranteed roles and the wolves
    roles = [PlayerRole.WOLF] * num_wolves
    roles += guaranteed_roles

    # Fill in the villagers
    roles += [PlayerRole.VILLAGER] * num_villagers

    # For the rest, pick from the optional roles
    # Prepare a list of optional roles and weightings
    remaining_roles_and_weights = role_weights.copy()

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
                remaining_slots = num_players - len(roles)

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
