import random

import pytest

from backend.model import PlayerRole
from backend.roles import assign_roles
from backend.roles.distribution import DistributionSettings
from backend.roles.distribution import DUAL_ROLES


def setup_module(module):
    # For determinism
    random.seed(123)


def test_basics():
    assert assign_roles(0, None) is None
    assert assign_roles(1, None) is None
    assert assign_roles(2, None) is None

    assert assign_roles(3, None) is not None
    assert assign_roles(4, None) is not None
    assert assign_roles(5, None) is not None
    assert assign_roles(10, None) is not None
    assert assign_roles(20, None) is not None
    assert assign_roles(100, None) is not None


@pytest.mark.parametrize("num_players", [3, 4, 5, 10, 20, 100])
def test_wolf_always_present(num_players):
    roles = assign_roles(num_players, None)

    assert any(r is PlayerRole.WOLF for r in roles)


@pytest.mark.parametrize("num_players", [3, 4, 5, 10, 20, 100])
def test_seer_always_present(num_players):
    roles = assign_roles(num_players, None)

    assert any(r is PlayerRole.SEER for r in roles)


@pytest.mark.parametrize("num_players", [5])
def test_num_villagers(num_players):

    settings = DistributionSettings(probability_of_villager=0.25)

    roles = []
    for _ in range(10):
        roles += assign_roles(num_players, settings)

    frac_villagers = sum(r is PlayerRole.VILLAGER for r in roles) / len(roles)

    assert 0.15 < frac_villagers < 0.35


def test_dual_roles_are_dual():

    num_players = 20
    num_repeats = 100

    settings = DistributionSettings(probability_of_villager=0.25)

    for _ in range(num_repeats):
        roles = assign_roles(num_players, settings)

        for r in DUAL_ROLES:
            if r in roles:
                assert roles.count(r) == 2


def test_dual_roles_assigned():

    num_players = 20
    num_repeats = 100

    dual_roles_seen = {r: False for r in DUAL_ROLES}

    settings = DistributionSettings(probability_of_villager=0.25)

    for _ in range(num_repeats):
        roles = assign_roles(num_players, settings)

        for r in DUAL_ROLES:
            if r in roles:
                dual_roles_seen[r] = True

    assert all(dual_roles_seen.values())
