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
    yield driver
    driver.close()


def test_homepage(driver):
    driver.get(TEST_URL)
    assert "Wurwolves" in driver.title
