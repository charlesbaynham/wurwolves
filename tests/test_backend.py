from fastapi.testclient import TestClient

from backend.game import WurwolvesGame
from backend.main import app

GAME_ID = "hot-potato"


def test_client(api_client):
    pass


def test_read_main(api_client):
    response = api_client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello world!"}


def test_join(api_client, db_session):
    g = WurwolvesGame(GAME_ID)
    assert g.get_game_model() is None
    response = api_client.post("/api/{}/join".format(GAME_ID))
    assert response.status_code == 200
    assert len(g.get_game_model().players) == 1


def test_state_speed(api_client_factory):
    import random
    from timeit import timeit

    g = WurwolvesGame(GAME_ID)

    num_players = 10
    num_repeats = 10

    clients = [api_client_factory() for _ in range(num_players)]

    # Join game
    for c in clients:
        rand_id = random.random()
        response = c.post(
            "/api/{}/join".format(GAME_ID), params={"temporary_id": rand_id}
        )

    # Render states
    def f():
        for c in clients:
            response = c.get("/api/{}/state".format(GAME_ID))
            assert response.ok

    total_time = timeit(f, number=num_repeats)

    time_per_render = total_time / (num_players * num_repeats)

    print(time_per_render)

    raise RuntimeError


def test_join_no_change_hash(api_client, db_session):
    g = WurwolvesGame(GAME_ID)
    api_client.post("/api/{}/join".format(GAME_ID))
    game_hash = g.get_hash_now()
    api_client.post("/api/{}/join".format(GAME_ID))
    assert game_hash == g.get_hash_now()


def test_keepalive_no_change_hash(api_client, db_session):
    g = WurwolvesGame(GAME_ID)

    api_client.post("/api/{}/join".format(GAME_ID))
    api_client.get("/api/{}/state_hash".format(GAME_ID))

    first_game_hash = g.get_hash_now()
    api_client.get("/api/{}/state_hash".format(GAME_ID))

    second_game_hash = g.get_hash_now()

    assert first_game_hash == second_game_hash
