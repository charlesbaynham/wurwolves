import re
import time

import geckodriver_autoinstaller
import pytest
import selenium
from selenium import webdriver

from backend.reset_db import reset_database

geckodriver_autoinstaller.install()


TEST_URL = "localhost:3000"
TEST_GAME = "james-doesnt-understand-prostitute"


@pytest.fixture(scope="session")
def session_driver():
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(TEST_URL)
    yield driver
    driver.close()


@pytest.fixture
def driver(session_driver):
    reset_database()
    return session_driver


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
