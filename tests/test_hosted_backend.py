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


# def test_multiple_state_requests(backend_server):
#     logging.getLogger("urllib3").setLevel(logging.WARNING)

#     # Make 10 sessions
#     num_players = 10

#     game_url = API_URL + "somegame/"

#     sessions = [requests.Session() for _ in range(num_players)]

#     start = time.time()

#     for s in sessions:
#         assert s.post(game_url + "join").ok

#         r = s.get(game_url + "state", timeout=10)

#     assert r.ok

#     state = json.loads(r.content)

#     logging.info("Joined game as %s, t=%.2fs", state["myName"], time.time() - start)

# # Start the game
# # sessions[0].post(game_url + "spectator_lobby_action", timeout=2)

# # end = time.time()
# # logging.info("Total time: %.2f", end - start)

# # start = time.time()

# # states = []
# # for s in sessions:
# try:
#     r = s.get(game_url + "state", timeout=5)
# except requests.exceptions.ReadTimeout:
#     raise RuntimeError("Timeout")

# assert r.ok

# states.append(r.content)

# end = time.time()
# logging.info("Total state rendering: %.2f", end - start)

# states = [json.loads(x) for x in states]

# raise RuntimeError
