import math
import random
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pydantic

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


class DistributionSettings(pydantic.BaseModel):
    number_of_wolves: Callable = None
    probability_of_villager: float = PROB_VILLAGER
    role_weights: Dict[PlayerRole, float] = RANDOMISED_ROLES

    @pydantic.validator("number_of_wolves", always=True)
    def num(cls, v, values):
        if v is None:
            return _default_num_wolves
        return v

    @pydantic.validator("probability_of_villager", always=True)
    def prob(cls, v, values):
        if v < 0 or v > 1:
            raise ValueError("probability_of_villager must be between 0 and 1")
        return v


def assign_roles(
    num_players: int, settings: Optional[DistributionSettings] = None
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

    probability_of_villager = settings.probability_of_villager
    num_wolves = settings.number_of_wolves(num_players)
    role_weights = settings.role_weights

    if num_players < len(guaranteed_roles) + 1:
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
