"""
These tests are run against a real server, using the server code defined in test_selenium
"""
import requests


API_URL = "http://localhost:3000/api/"


def test_hello(test_server):
    print(requests.get(API_URL + "hello"))
    raise RuntimeError


def test_print():
    import sys

    print(sys.path)
    # raise RuntimeError
