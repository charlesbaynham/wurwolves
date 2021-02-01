"""
These tests are run against a real server, using the server code defined in test_selenium
"""
import json
import logging
import time

import requests

API_URL = "http://localhost:8000/api/"
READ_TIMEOUT = 5


def test_hello(backend_server):
    response = requests.get(API_URL + "hello")

    print(response.status_code)
    print(response.content)

    assert response.ok


def test_multiple_state_requests(backend_server):
    from timeit import timeit

    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Make 10 sessions
    num_players = 10

    game_url = API_URL + "somegame/"

    sessions = [requests.Session() for _ in range(num_players)]

    start = time.time()

    states = []

    for s in sessions:
        r = s.post(game_url + "join", timeout=READ_TIMEOUT)
        assert r.ok

        r = s.get(game_url + "state", timeout=READ_TIMEOUT)
        assert r.ok

        states.append(r.content)

    logging.info(
        "%sx joins and renders in t=%.0fms per player",
        num_players,
        1000 * (time.time() - start) / num_players,
    )

    # Start the game
    time_to_start = timeit(
        lambda: sessions[0].post(
            game_url + "spectator_lobby_action", timeout=READ_TIMEOUT
        ),
        number=1,
    )

    logging.info("%.0fms to start game", time_to_start * 1000)

    # Render states again
    def render():
        states = []
        for s in sessions:
            r = s.get(game_url + "state", timeout=READ_TIMEOUT)
            states.append(r.content)
        return states

    time_to_render = timeit(render, number=1) / num_players

    logging.info("%.0fms to render states after game started", 1000 * time_to_render)
