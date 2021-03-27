import json
import logging
import random
import time

from fastapi.testclient import TestClient

from backend.game import WurwolvesGame
from backend.main import app
from backend.model import DistributionSettings
from backend.model import GameStage
from backend.model import PlayerRole

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


def _get_database_times(logs):
    times = [l.args[0] for l in logs if "Query complete" in l.msg]
    assert len(times) > 0
    return times


def test_state_speed(api_client_factory, caplog):
    caplog.set_level(logging.DEBUG, logger="sqltimings")

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

    join_logs = caplog.records
    caplog.clear()

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

    render_logs = caplog.records

    num_joins = num_players
    num_renders = num_players * num_repeats

    join_database_times = _get_database_times(join_logs)
    render_database_times = _get_database_times(render_logs)

    time_per_join = (end_joins - start_joins) / num_joins
    time_per_render = (end_renders - start_renders) / num_renders

    logging.warning(
        f"time_per_join = {time_per_join:.3f}s of which "
        f"{sum(join_database_times) / num_joins:.3f}s in "
        f"{len(join_database_times)/num_joins} DB calls"
    )
    logging.warning(
        f"time_per_render = {time_per_render:.3f}s of which "
        f"{sum(render_database_times) / num_renders:.3f}s in "
        f"{len(render_database_times)/num_renders} DB calls"
    )

    assert time_per_join < 0.1
    assert time_per_render < 0.1


def test_single_render(api_client_factory, caplog):
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="sqltimings")

    num_players = 10

    clients = [api_client_factory() for _ in range(num_players)]
    rand_ids = [random.random() for _ in clients]

    # Join game
    for c, rand_id in zip(clients, rand_ids):
        response = c.post(
            "/api/{}/join".format(GAME_ID), params={"temporary_id": rand_id}
        )

    # Send a few messages
    messages = [
        "Hello world!",
        "This is going to be fun",
        "Guys, how does the prostitute work?",
    ]
    g = WurwolvesGame(GAME_ID)
    for m in messages:
        g.send_chat_message(m)

    # Render states
    rand_id = rand_ids[0]
    c = clients[0]

    caplog.clear()

    start = time.time()
    response = c.get("/api/{}/state".format(GAME_ID), params={"temporary_id": rand_id})
    total_time = time.time() - start

    render_logs = caplog.records

    render_database_times = _get_database_times(render_logs)

    assert response.ok

    logging.warning(f"total_time = {total_time:.3f}s")

    logging.warning(
        f"total_time = {total_time:.3f}s of which "
        f"{sum(render_database_times):.3f}s in "
        f"{len(render_database_times)} DB calls"
    )

    assert total_time < 0.1


def test_rejoin_no_change_hash(api_client, db_session):
    """
    Rejoining a game you're already in shouldn't update everyone's state
    """
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


def test_get_default_role_weights(api_client):
    from backend.model import DistributionSettings

    r = api_client.get("/api/default_role_weights")

    print(r.content)

    assert r.ok


def test_get_game_config_mode(api_client, db_session):
    from backend.model import DistributionSettings

    r = api_client.get(f"/api/{GAME_ID}/game_config_mode")
    assert r.ok

    assert json.loads(r.content) == "hard"


def test_set_get_game_config_mode(api_client, db_session):
    from urllib.parse import urlencode

    api_client.post(f"/api/{GAME_ID}/join")
    r = api_client.get(f"/api/{GAME_ID}/game_config_mode")

    config = json.loads(r.content)

    assert config == "hard"

    r = api_client.post(
        f"/api/{GAME_ID}/game_config_mode?" + urlencode({"new_config_mode": "easy"})
    )

    assert r.ok

    r = api_client.get(f"/api/{GAME_ID}/game_config_mode")
    assert r.ok
    config2 = json.loads(r.content)

    assert config2 == "easy"


def test_end_game(api_client, db_session):
    from uuid import uuid4 as uuid

    g = WurwolvesGame(GAME_ID)

    with api_client as s:
        r = s.post(f"/api/{GAME_ID}/join")
        assert r.ok

        for _ in range(4):
            g.join(uuid())

        g.start_game()

        assert g.get_game_model().stage == GameStage.NIGHT

        r = s.post(f"/api/{GAME_ID}/end_game")
        assert r.ok

        assert g.get_game_model().stage == GameStage.ENDED
