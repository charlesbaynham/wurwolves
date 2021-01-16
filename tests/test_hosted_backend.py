"""
These tests are run against a real server, using the server code defined in test_selenium
"""
import json
import logging
import time

import requests

API_URL = "http://localhost:8000/api/"


def test_hello(backend_server):
    response = requests.get(API_URL + "hello")

    print(response.status_code)
    print(response.content)

    assert response.ok


def test_multiple_state_requests(backend_server):

    # Make 10 sessions
    num_players = 10

    game_url = API_URL + "somegame/"

    sessions = [requests.Session() for _ in range(num_players)]

    for s in sessions:
        with s:
            assert s.post(game_url + "join").ok

            r = s.get(game_url + "state")

            print(r.status_code)
            print(r.content)

            assert r.ok

            state = json.loads(r.content)

            logging.info("Joined game as %s", state["myName"])

    # Start the game
    # with sessions[0] as s:
    #     s.

    # raise RuntimeError
