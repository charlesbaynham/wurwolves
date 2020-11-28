import re

import geckodriver_autoinstaller
import pytest
import selenium
from selenium import webdriver

geckodriver_autoinstaller.install()  # Check if the current version of geckodriver exists
# and if it doesn't exist, download it automatically,
# then add geckodriver to path


TEST_URL = "localhost:3000"


@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Firefox()
    driver.get(TEST_URL)
    yield driver
    driver.close()


def test_homepage(driver):
    assert "Wurwolves" in driver.title


def test_start_game(driver):

    button = driver.find_element_by_css_selector("#home-content-box button")

    button.click()

    print(f"url = {driver.current_url}")

    game_name = re.search(r"(\w+-\w+-\w+-\w+)", driver.current_url)[1]
    print(f"game_name = {game_name}")
