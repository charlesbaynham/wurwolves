"""
These tests are run against a real server, using the server code defined in test_selenium
"""
import time

import requests

API_URL = "http://localhost:8000/api/"


def test_hello(backend_server):

    response = requests.get(API_URL + "hello")

    print(response.status_code)
    print(response.content)

    assert response.ok


def test_hello2(backend_server):

    response = requests.get(API_URL + "hello")

    print(response.status_code)
    print(response.content)

    assert response.ok
