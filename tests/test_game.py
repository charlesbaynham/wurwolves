

from uuid import uuid4 as uuid

from backend.game import WurwolvesGame
from backend.model import (Game, GameStage, Player, PlayerRole, PlayerState,
                           User, hash_game_id)

GAME_ID = "hot-potato"
USER_ID = uuid()


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

    g.start_game()

    db_session.expire_all()

    assert db_game.stage == GameStage.NIGHT

    p: Player
    for p in db_game.players:
        assert p.state == PlayerState.ALIVE

    new_user_id = uuid()
    g.join(new_user_id)
    db_session.expire_all()

    p = get_player(db_session, GAME_ID, new_user_id)

    assert p.role == PlayerRole.SPECTATOR


def get_game(db_session, id) -> Game:
    return (db_session
            .query(Game)
            .filter(Game.id == hash_game_id(id))
            .first())


def get_player(db_session, game_id, user_id) -> Game:
    return (db_session
            .query(Player)
            .filter(
                Player.game_id == hash_game_id(game_id),
                Player.user_id == user_id
            )
            .first())
