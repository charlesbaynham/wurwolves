import concurrent.futures
import logging
import os
import re
import time
from multiprocessing import Pool

import geckodriver_autoinstaller
import pytest
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.reset_db import reset_database


def setup_module(module):
    logging.getLogger().setLevel(logging.WARNING)
    try:
        geckodriver_autoinstaller.install()
    except RuntimeError:
        logging.error("Could not install geckodriver: continuing anyway")


TEST_URL = "localhost:3000"
TEST_GAME = "james-doesnt-understand-prostitute"
from pathlib import Path


# Mark this whole module as requiring selenium
pytestmark = pytest.mark.selenium


@pytest.fixture(scope="session")
def session_driver(full_server):
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
    session_driver.delete_all_cookies()


def make_drv(*args):
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    return driver


def make_N_drivers(n, url=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        drivers = list(executor.map(make_drv, range(n)))

    if url:
        for d in drivers:
            d.get(url)

    return drivers


@pytest.fixture(scope="session")
def five_drivers_raw(full_server):
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
        d.delete_all_cookies()


def test_homepage(driver):
    assert "Wurwolves" in driver.title


def test_start_game(driver):
    button = driver.find_element_by_css_selector("#home-content-box button")

    button.click()

    print(f"url = {driver.current_url}")

    game_name = re.search(r"(\w+-\w+-\w+-\w+)", driver.current_url)
    assert game_name
    print(f"game_name = {game_name[1]}")


def set_name(driver, name):
    driver.get(f"{TEST_URL}/{TEST_GAME}")
    name_box = driver.find_element_by_xpath("//nav//input")

    name_box.send_keys(name)
    name_box.submit()


def get_store(driver):
    return driver.execute_script("return window.store.getState();")


def test_set_name(driver):
    my_name = "My name"

    set_name(driver, my_name)

    time.sleep(0.5)

    xpath_players = "//*[@id='playerGrid']//figure"

    wait = WebDriverWait(driver, 3)
    players = wait.until(
        EC.text_to_be_present_in_element((By.XPATH, xpath_players), my_name)
    )

    players = driver.find_elements_by_xpath(xpath_players)
    assert len(players) == 1


def test_multiple_players(five_drivers):
    my_driver = five_drivers[-1]
    my_name = "The first one"

    set_name(my_driver, my_name)

    time.sleep(1)

    for driver in five_drivers:
        players = my_driver.find_elements_by_xpath("//*[@id='playerGrid']//figure")

        assert len(players) == 5
        assert any(my_name in p.text for p in players)

    store = get_store(my_driver)
    players_store = store["backend"]["players"]

    print(f"Store: {store}")
    print(f"Players: {players_store}")


def test_api_state_hash(five_drivers):
    for d in five_drivers:
        d.get(f"{TEST_URL}/api/{TEST_GAME}/state_hash")
        print(d.page_source)


def test_game_starts_ok(five_drivers):
    for d in five_drivers:
        d.get(f"{TEST_URL}/{TEST_GAME}")
        button = d.find_element_by_id("actionButton")
        assert "Start game" in button.text

    button.click()

    time.sleep(2)

    chat = five_drivers[0].find_element_by_css_selector(".chat-box")
    assert "new game has started" in chat.text

    medic_driver = None
    for d in five_drivers:
        try:
            button = d.find_element_by_id("actionButton")
            if "someone to save" in button.text:
                medic_driver = d
                break
        except selenium.common.exceptions.NoSuchElementException:
            pass

    assert medic_driver, "No medic found"

    assert button.get_property("disabled") is False

    button.click()
    time.sleep(1)
    assert button.get_property("disabled") is False

    medic_driver.find_element_by_css_selector(".playerWrapperOuter").click()
    time.sleep(0.5)
    button.click()
    time.sleep(2)
    assert button.get_property("disabled") is True
