import logging
import random
import time

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


def test_state_speed(api_client_factory, caplog):
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.INFO, logger="sqlalchemy.engine")

    g = WurwolvesGame(GAME_ID)

    num_players = 10
    num_repeats = 1

    clients = [api_client_factory() for _ in range(num_players)]
    rand_ids = [random.random() for _ in clients]

    # Join game
    start_joins = time.time()
    for c, rand_id in zip(clients, rand_ids):
        response = c.post(
            "/api/{}/join".format(GAME_ID), params={"temporary_id": rand_id}
        )
    end_joins = time.time()

    # Render states
    start_renders = time.time()
    for i_repeat in range(num_repeats):
        for i_client, (c, rand_id) in enumerate(zip(clients, rand_ids)):
            logging.info("Repeat %s, client %s", i_repeat, i_client)
            try:
                response = c.get(
                    "/api/{}/state".format(GAME_ID), params={"temporary_id": rand_id}
                )
                assert response.ok
            except Exception as e:
                logging.error("Failed at repeat %s, client %s", i_repeat, i_client)
                raise e

    end_renders = time.time()

    time_per_join = (end_joins - start_joins) / (num_players * num_repeats)
    time_per_render = (end_renders - start_renders) / (num_players * num_repeats)

    logging.warning(f"time_per_join = {time_per_join:.3f}s")
    logging.warning(f"time_per_render = {time_per_render:.3f}s")

    assert time_per_join < 0.1
    assert time_per_render < 0.1


def test_single_render(api_client_factory, caplog):
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.INFO, logger="sqlalchemy.engine")

    g = WurwolvesGame(GAME_ID)

    num_players = 10

    clients = [api_client_factory() for _ in range(num_players)]
    rand_ids = [random.random() for _ in clients]

    # Join game
    for c, rand_id in zip(clients, rand_ids):
        response = c.post(
            "/api/{}/join".format(GAME_ID), params={"temporary_id": rand_id}
        )

    # Render states
    start = time.time()

    rand_id = rand_ids[0]
    c = clients[0]

    try:
        response = c.get(
            "/api/{}/state".format(GAME_ID), params={"temporary_id": rand_id}
        )
        assert response.ok
    except Exception as e:
        logging.error("Failed at repeat %s, client %s", i_repeat, i_client)
        raise e

    total_time = time.time() - start

    logging.warning(f"total_time = {total_time:.3f}s")

    assert total_time < 0.1


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
