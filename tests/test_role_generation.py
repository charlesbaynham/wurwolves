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


import itertools


@pytest.mark.parametrize(
    "num_players,num_wolves", itertools.product(range(20), range(20))
)
def test_customization_num_wolves(num_players, num_wolves):
    settings = DistributionSettings(number_of_wolves=num_wolves)
    roles = assign_roles(num_players, settings)

    if num_players >= num_wolves + 2:
        assert len([r for r in roles if r is PlayerRole.WOLF]) == num_wolves
    else:
        assert roles is None


@pytest.mark.parametrize("num_players", range(3, 20))
def test_customization_no_roles(num_players):
    settings = DistributionSettings(probability_of_villager=1)
    roles = assign_roles(num_players, settings)

    allowed_roles = [
        PlayerRole.WOLF,
        PlayerRole.VILLAGER,
        PlayerRole.SEER,
        PlayerRole.MEDIC,
    ]

    assert all([r in allowed_roles for r in roles])


@pytest.mark.parametrize("num_players", range(4, 20))
def test_customize_roles(num_players):
    settings = DistributionSettings(
        role_weights={
            PlayerRole.ACOLYTE: 1,
        },
        probability_of_villager=0,
    )
    roles = assign_roles(num_players, settings)

    required_roles = [
        PlayerRole.WOLF,
        PlayerRole.SEER,
        PlayerRole.MEDIC,
        PlayerRole.ACOLYTE,
    ]
    possible_roles = [PlayerRole.VILLAGER]

    assert all([r in required_roles + possible_roles for r in roles])
    assert all([r in roles for r in required_roles])


@pytest.mark.parametrize("num_players", range(5, 20))
def test_customize_roles_2(num_players):
    settings = DistributionSettings(
        role_weights={PlayerRole.ACOLYTE: 1, PlayerRole.JESTER: 1, PlayerRole.FOOL: 0},
        probability_of_villager=0,
    )
    roles = assign_roles(num_players, settings)

    required_roles = [
        PlayerRole.WOLF,
        PlayerRole.SEER,
        PlayerRole.MEDIC,
        PlayerRole.ACOLYTE,
        PlayerRole.JESTER,
    ]
    possible_roles = [PlayerRole.VILLAGER]

    assert all([r in required_roles + possible_roles for r in roles])
    assert all([r in roles for r in required_roles])


@pytest.mark.parametrize("num_players", range(5, 20))
def test_customize_roles_3(num_players):
    settings = DistributionSettings(
        role_weights={PlayerRole.MASON: 1}, probability_of_villager=0
    )
    roles = assign_roles(num_players, settings)

    required_roles = [
        PlayerRole.WOLF,
        PlayerRole.SEER,
        PlayerRole.MEDIC,
        PlayerRole.MASON,
    ]
    possible_roles = [PlayerRole.VILLAGER]

    assert all([r in required_roles + possible_roles for r in roles])
    assert all([r in roles for r in required_roles])
