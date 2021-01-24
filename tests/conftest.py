import logging
import os

import pytest

logging.basicConfig(level=logging.DEBUG)

# Shared fixtures:
from .shared_fixtures import *


def pytest_addoption(parser):
    parser.addoption(
        "--runselenium", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "selenium: marks tests as requiring selenium (select with '-m selenium')",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runselenium"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_selenium = pytest.mark.skip(reason="need --runselenium option to run")
    for item in items:
        if "selenium" in item.keywords:
            item.add_marker(skip_selenium)
