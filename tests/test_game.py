from datetime import datetime
from uuid import uuid4 as uuid

import pytest

from backend.game import WurwolvesGame
from backend.model import (
    Game,
    GameStage,
    Player,
    PlayerRole,
    PlayerState,
    User,
    hash_game_tag,
)

GAME_ID = "hot-potato"
USER_ID = uuid()
PLAYER_NAME = "Charles"


def test_add_player(db_session):
    g = WurwolvesGame(GAME_ID)
    g.join(USER_ID)

    assert len(db_session.query(Game).all()) == 1
    assert len(db_session.query(User).all()) == 1
    db_game = db_session.query(Game).first()
    assert len(db_session.query(Player).filter(Player.game == db_game).all()) == 1

    g.join(uuid())

    assert len(db_session.query(Game).all()) == 1
    assert len(db_session.query(User).all()) == 2
    assert len(db_session.query(Player).filter(Player.game == db_game).all()) == 2

    g.join(USER_ID)

    assert len(db_session.query(Game).all()) == 1
    assert len(db_session.query(User).all()) == 2
    assert len(db_session.query(Player).filter(Player.game == db_game).all()) == 2


def test_name_player(db_session):
    g = WurwolvesGame(GAME_ID)
    g.join(USER_ID)

    assert len(db_session.query(User).all()) == 1
    u = db_session.query(User).filter(User.id == USER_ID).first()
    assert u.name_is_generated

    g.set_player(USER_ID, "Charles")
    db_session.expire_all()

    u = db_session.query(User).filter(User.id == USER_ID).first()
    assert not u.name_is_generated
    assert u.name == "Charles"


def test_start_game(db_session):
    g = WurwolvesGame(GAME_ID)
    g.join(USER_ID)
    g.join(uuid())
    g.join(uuid())

    db_game = get_game(db_session, GAME_ID)

    assert db_game.stage == GameStage.LOBBY

    p: Player
    for p in db_game.players:
        assert p.role == PlayerRole.SPECTATOR
        assert p.state == PlayerState.SPECTATING

    g.start_game()

    db_session.expire_all()

    assert db_game.stage == GameStage.NIGHT

    p: Player
    for p in db_game.players:
        assert p.role != PlayerRole.SPECTATOR
        assert p.state == PlayerState.ALIVE

    new_user_id = uuid()
    g.join(new_user_id)
    db_session.expire_all()

    p = get_player(db_session, GAME_ID, new_user_id)

    assert p.role == PlayerRole.SPECTATOR


def test_keepalive(demo_game, db_session):
    demo_game.player_keepalive(USER_ID)


def test_kill(demo_game, db_session):
    player_id = demo_game.get_player_id(USER_ID)

    p = demo_game.get_player_model(USER_ID)
    assert p.previous_role is None

    demo_game.kill_player(player_id, PlayerState.LYNCHED)

    db_session.expire_all()

    p = demo_game.get_player_model(USER_ID)
    assert p.previous_role is not None


def test_chat(demo_game, db_session):
    other_user = uuid()
    demo_game.join(other_user)

    demo_game.send_chat_message("Hello world!")
    demo_game.send_chat_message("Important", is_strong=True)
    demo_game.send_chat_message("Secret", user_list=[USER_ID])
    demo_game.send_chat_message("Secret 2", user_list=[other_user])

    db_session.expire_all()

    visible_messages = demo_game.get_messages(USER_ID)

    from json import dumps

    summary = dumps([v.dict() for v in visible_messages])

    assert "Hello world!" in summary
    assert "Important" in summary
    assert "Secret" in summary
    assert "Secret 2" not in summary


def test_chat_order(demo_game, db_session):
    # Clear current messages
    demo_game.clear_chat_messages()

    messages_text = [
        "Message 1",
        "Message 2",
        "Message 3",
        "Message 4",
    ]

    for txt in messages_text:
        demo_game.send_chat_message(txt)

    db_session.expire_all()

    game = demo_game.get_game()
    db_session.add(game)

    for message, sent_text in zip(game.messages, messages_text):
        assert message.text == sent_text


def test_chat_order_deletions(demo_game, db_session):
    # Clear current messages
    demo_game.clear_chat_messages()

    demo_game.send_chat_message("To be deleted")

    messages_text = [
        "Message 1",
        "Message 2",
        "Message 3",
        "Message 4",
    ]

    for txt in messages_text:
        demo_game.send_chat_message(txt)

    db_session.expire_all()
    game = demo_game.get_game()
    db_session.add(game)

    db_session.delete(game.messages[0])
    db_session.commit()
    db_session.expire_all()

    demo_game.send_chat_message("Final")

    for message, sent_text in zip(game.messages, messages_text + ["Final"]):
        assert message.text == sent_text


def get_game(db_session, id) -> Game:
    return db_session.query(Game).filter(Game.id == hash_game_tag(id)).first()


def get_player(db_session, game_id, user_id) -> Game:
    return (
        db_session.query(Player)
        .filter(Player.game_id == hash_game_tag(game_id), Player.user_id == user_id)
        .first()
    )


@pytest.fixture
def demo_game(db_session) -> WurwolvesGame:
    g = WurwolvesGame(GAME_ID)

    # You need at least three players for start_game() to work
    g.join(USER_ID)
    g.join(uuid())
    g.join(uuid())

    return g


def test_async_get_hash_msg(db_session, demo_game):
    import asyncio

    async def tester():
        initial_hash = demo_game.get_hash_now()

        task_waiter = asyncio.ensure_future(demo_game.get_hash(known_hash=initial_hash))

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        demo_game.get_player_model(USER_ID)

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        demo_game.send_chat_message("Hello world")

        await asyncio.sleep(0.1)
        assert task_waiter.done()

    asyncio.get_event_loop().run_until_complete(tester())


def test_async_get_hash_name(db_session, demo_game):
    import asyncio

    async def tester():
        initial_hash = demo_game.get_hash_now()

        task_waiter = asyncio.ensure_future(demo_game.get_hash(known_hash=initial_hash))

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        demo_game.get_player_model(USER_ID)

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        WurwolvesGame.set_user_name(USER_ID, "Something else")

        await asyncio.sleep(0.1)
        assert task_waiter.done()

    asyncio.get_event_loop().run_until_complete(tester())


def test_async_get_start_game(db_session, demo_game):
    import asyncio

    async def tester():
        initial_hash = demo_game.get_hash_now()

        task_waiter = asyncio.ensure_future(demo_game.get_hash(known_hash=initial_hash))

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        demo_game.get_player_model(USER_ID)

        await asyncio.sleep(0.1)
        assert not task_waiter.done()

        demo_game.start_game()

        await asyncio.sleep(0.1)
        assert task_waiter.done()

    asyncio.get_event_loop().run_until_complete(tester())


def test_kick(db_session):
    game = WurwolvesGame(GAME_ID)

    # Add three players
    player_ids = [uuid() for _ in range(3)]
    for p in player_ids:
        game.join(p)

    # Set one to have joined ages ago
    timeout_player_id = player_ids[0]
    timeout_player = game.get_player(timeout_player_id)
    db_session.add(timeout_player)

    timeout_player.last_seen = datetime(1, 1, 1)

    db_session.commit()
    db_session.expire_all()

    timeout_player = game.get_player(timeout_player_id)
    db_session.add(timeout_player)

    assert timeout_player.state == PlayerState.SPECTATING

    # Keepalive one of the other players, which should kick the idler
    game.player_keepalive(player_ids[1])

    db_session.expire_all()

    assert not game.get_player(timeout_player_id)


def test_kick_with_actions(db_session):
    game = WurwolvesGame(GAME_ID)

    # Add three players
    player_ids = [uuid() for _ in range(3)]
    roles = [
        PlayerRole.VILLAGER,
        PlayerRole.VILLAGER,
        PlayerRole.WOLF,
    ]
    for p in player_ids:
        game.join(p)

    game.start_game()

    for p, r in zip(player_ids, roles):
        game.set_player_role(game.get_player_id(p), r)

    # Set one to have joined ages ago
    timeout_player_id = player_ids[0]
    wolf_id = player_ids[2]
    timeout_player = game.get_player(timeout_player_id)
    db_session.add(timeout_player)

    timeout_player.last_seen = datetime(1, 1, 1)

    db_session.commit()
    db_session.expire_all()

    timeout_player = game.get_player(timeout_player_id)
    db_session.add(timeout_player)

    assert timeout_player.state == PlayerState.ALIVE

    # Keepalive one of the other players, which should not kick the idler since it's a game
    game.player_keepalive(wolf_id)

    db_session.expire_all()
    assert game.get_player(timeout_player_id)

    # Kill the idler with the wolf
    game.wolf_night_action(wolf_id, timeout_player_id)

    db_session.expire_all()

    # Check game ended
    assert game.get_game_model().stage == GameStage.ENDED

    # Kick the idler
    game.player_keepalive(wolf_id)

    # Check they went
    db_session.expire_all()
    assert not game.get_player(timeout_player_id)


# @pytest.mark.parametrize("num_prev_stages", [0, 1, 2, 3, 5, 10])
# def test_num_previous_stages(demo_game, num_prev_stages):
#     demo_game._set_stage(GameStage.DAY)

#     for i in range(num_prev_stages):
#         demo_game._set_stage(GameStage.NIGHT)

#     assert demo_game.num_previous_stages(GameStage.NIGHT) == num_prev_stages
#     assert (
#         demo_game.num_previous_stages(
#             GameStage.NIGHT, demo_game.get_game_model().stage_id
#         )
#         == num_prev_stages - 1
#     )
