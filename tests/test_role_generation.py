import random

import pytest

from backend.model import PlayerRole
from backend.roles import assign_roles


# For determinism
random.seed(123)


def test_basics():
    assert assign_roles(0) is None
    assert assign_roles(1) is None
    assert assign_roles(2) is None

    assert assign_roles(3) is not None
    assert assign_roles(4) is not None
    assert assign_roles(5) is not None
    assert assign_roles(10) is not None
    assert assign_roles(20) is not None
    assert assign_roles(100) is not None


@pytest.mark.parametrize("num_players", [3, 4, 5, 10, 20, 100])
def test_wolf_always_present(num_players):
    roles = assign_roles(num_players)

    assert any(r is PlayerRole.WOLF for r in roles)


@pytest.mark.parametrize("num_players", [3, 4, 5, 10, 20, 100])
def test_seer_always_present(num_players):
    roles = assign_roles(num_players)

    assert any(r is PlayerRole.SEER for r in roles)


@pytest.mark.parametrize("num_players", [5])
def test_num_villagers(num_players):

    roles = []
    for _ in range(10):
        roles += assign_roles(num_players, probability_of_villager=0.25)

    frac_villagers = sum(r is PlayerRole.VILLAGER for r in roles) / len(roles)

    assert 0.15 < frac_villagers < 0.35
