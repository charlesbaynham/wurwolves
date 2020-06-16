import pytest

from backend.model import PlayerRole
from backend.roles import assign_roles


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
