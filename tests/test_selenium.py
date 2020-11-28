import re
import time
from multiprocessing import Pool

import geckodriver_autoinstaller
import pytest
import selenium
from selenium import webdriver

from backend.reset_db import reset_database

geckodriver_autoinstaller.install()


TEST_URL = "localhost:3000"
TEST_GAME = "james-doesnt-understand-prostitute"

# Mark this whole module as requiring selenium
pytestmark = pytest.mark.selenium


@pytest.fixture(scope="session")
def test_server():
    # Later, this should launch and close a test server
    pass


@pytest.fixture(scope="session")
def session_driver(test_server):
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    yield driver
    driver.close()


@pytest.fixture
def driver(session_driver):
    reset_database()
    session_driver.get(TEST_URL)
    yield session_driver
    session_driver.get("about:blank")


def make_drv(*args):
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    return driver


@pytest.fixture(scope="session")
def five_drivers_raw(test_server):
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        drivers = list(executor.map(make_drv, range(5)))

    yield drivers

    for d in drivers:
        d.close()


@pytest.fixture
def five_drivers(five_drivers_raw):
    reset_database()
    for d in five_drivers_raw:
        d.get(f"{TEST_URL}/{TEST_GAME}")

    yield five_drivers_raw

    for d in five_drivers_raw:
        d.get("about:blank")


def test_homepage(driver):
    assert "Wurwolves" in driver.title


def test_start_game(driver):
    button = driver.find_element_by_css_selector("#home-content-box button")

    button.click()

    print(f"url = {driver.current_url}")

    game_name = re.search(r"(\w+-\w+-\w+-\w+)", driver.current_url)[1]
    assert game_name
    print(f"game_name = {game_name}")


def test_set_name(driver):

    TEST_NAME = "My name"

    driver.get(f"{TEST_URL}/{TEST_GAME}")
    name_box = driver.find_element_by_xpath("//nav//input")

    name_box.send_keys(TEST_NAME)
    name_box.submit()

    players = driver.find_elements_by_xpath("//*[@id='playerGrid']//figure")

    assert len(players) == 1
    assert players[0].text == TEST_NAME


def test_multiple_players(five_drivers):
    players = five_drivers[-1].find_elements_by_xpath("//*[@id='playerGrid']//figure")

    assert len(players) == 5
