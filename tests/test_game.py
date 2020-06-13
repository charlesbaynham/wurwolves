

from uuid import uuid4 as uuid

from backend.game import WurwolvesGame
from backend.model import Game, Player, User

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
