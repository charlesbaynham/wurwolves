# from backend.model import GameEvent, EventType, hash_game_id
# from backend.events import EventQueue
# from uuid import uuid4 as uuid
# from backend.game import WurwolvesGame


# GAME_ID = "hot-potato"
# USER_ID = uuid()


# def test_client(client):
#     pass


# def test_read_main(api_client):
#     response = api_client.get("/api/hello")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello world!"}


# def test_set_player(api_client, db_session):
#     response = api_client.post("/api/{}/join".format(GAME_ID), params={'name': 'Charles'})
#     assert response.status_code == 200

#     assert (db_session
#             .query(GameEvent)
#             .filter(GameEvent.game_id == hash_game_id(GAME_ID))
#             .filter(GameEvent.event_type == EventType.UPDATE_PLAYER)
#             ).count() == 1

#     assert (db_session
#             .query(GameEvent)
#             .filter(GameEvent.game_id == hash_game_id(GAME_ID))
#             .filter(GameEvent.event_type == EventType.GUI)
#             ).count() == 1

#     response = api_client.post("/api/{}/join".format(GAME_ID), params={'name': 'Gaby'})
#     assert response.status_code == 200

#     assert (db_session
#             .query(GameEvent)
#             .filter(GameEvent.game_id == hash_game_id(GAME_ID))
#             .filter(GameEvent.event_type == EventType.GUI)
#             ).count() == 2

#     assert all(
#         db_session
#         .query(GameEvent.public_visibility)
#         .filter(GameEvent.game_id == hash_game_id(GAME_ID))
#         .filter(GameEvent.event_type == EventType.GUI)
#         .all()
#     )

#     q = EventQueue(GAME_ID, type_filter=EventType.UPDATE_PLAYER)
#     assert len(q.get_all_events()) == 2

#     q2 = EventQueue("another-game", type_filter=EventType.UPDATE_PLAYER)
#     assert len(q2.get_all_events()) == 0


# def test_ui_events(api_client, db_session):
#     response = api_client.get("/api/{}/ui_events".format(GAME_ID))
#     assert response.status_code == 200
#     assert len(response.json()) == 0

#     response = api_client.post("/api/{}/join".format(GAME_ID), params={'name': 'Charles'})
#     assert response.status_code == 200

#     response = api_client.get("/api/{}/ui_events".format(GAME_ID))
#     assert response.status_code == 200
#     data = response.json()

#     assert "event_type" not in response.content.decode()
#     assert data[0]['details']['payload']['name'] == 'Charles'
#     assert data[0]['details']['payload']['status'] == 'spectating'


# def test_newest_id(api_client, db_session):
#     response = api_client.get("/api/{}/newest_id".format(GAME_ID))
#     assert response.status_code == 200
#     assert response.json() == 0

#     g = WurwolvesGame(GAME_ID, USER_ID)
#     g.set_player(name="Charles", status="spectating")

#     latest_id = EventQueue(GAME_ID).get_latest_event_id()

#     response = api_client.get("/api/{}/newest_id".format(GAME_ID))
#     assert response.status_code == 200
#     assert response.json() == latest_id
