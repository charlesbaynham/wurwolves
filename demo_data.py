from uuid import uuid4 as uuid

from backend.database import session_scope
from backend.model import Game
from backend.model import Message
from backend.model import Player
from backend.model import PlayerRole
from backend.model import PlayerState
from backend.model import User


def make_data():
    with session_scope() as s:
        u = User(id=uuid(), name="Charles")
        g = Game()
        p = Player(role=PlayerRole.SEER, state=PlayerState.ALIVE)
        p.user = u
        p.game = g
        s.add(u)
        s.add(u)
        s.add(p)

        m = Message(text="hello")
        m.game = g
        m.visible_to.append(u)

        s.add(m)


if __name__ == "__main__":
    make_data()
