# from fastapi.testclient import TestClient
# from backend.game import WurwolvesGame
# from backend.main import app
# GAME_ID = "hot-potato"
# def test_client(api_client):
#     pass
# def test_read_main(api_client):
#     response = api_client.get("/api/hello")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello world!"}
# def test_join(api_client, db_session):
#     response = api_client.post("/api/{}/join".format(GAME_ID))
#     assert response.status_code == 200
#     g = WurwolvesGame(GAME_ID)
#     assert len(g.get_game().players) == 1
