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


def test_join_no_change_hash(api_client, db_session):
    g = WurwolvesGame(GAME_ID)
    api_client.post("/api/{}/join".format(GAME_ID))
    game_hash = g.get_hash_now()
    api_client.post("/api/{}/join".format(GAME_ID))
    assert game_hash == g.get_hash_now()


def test_keepalive_no_change_hash(api_client, db_session):
    g = WurwolvesGame(GAME_ID)

    api_client.post("/api/{}/join".format(GAME_ID))
    api_client.query("/api/{}/state_hash".format(GAME_ID))

    game_hash = g.get_hash_now()
    api_client.query("/api/{}/state_hash".format(GAME_ID))

    assert game_hash == g.get_hash_now()
