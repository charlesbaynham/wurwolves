import enum
import hashlib
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, TypeDecorator
from sqlalchemy_utils import UUIDType

Base = declarative_base()


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    See
    https://docs.sqlalchemy.org/en/13/core/custom_types.html#marshal-json-strings

    Usage::
        JSONEncodedDict(255)
    """

    impl = VARCHAR

    class UUIDEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, UUID):
                # if the obj is uuid, we simply return the value of uuid
                return obj.hex
            return json.JSONEncoder.default(self, obj)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, cls=self.UUIDEncoder)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Game(Base):
    """The current state of a game"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    created = Column(DateTime, default=datetime.utcnow())

    players = relationship(
        'Player', backref='game', lazy=True
    )

    messages = relationship(
        'Message', backref='game', lazy=True
    )

    def __repr__(self):
        return '<Game id={}, players={}>'.format(self.id, self.players)


class PlayerRole(enum.Enum):
    VILLAGER = 'VILLAGER'
    WOLF = 'WOLF'
    SEER = 'SEER'
    MEDIC = 'MEDIC'
    SPECTATOR = 'SPECTATOR'


class PlayerState(enum.Enum):
    ALIVE = 'ALIVE'
    WOLFED = 'WOLFED'
    LYNCHED = 'LYNCHED'
    NOMINATED = 'NOMINATED'
    SECONDED = 'SECONDED'


class Player(Base):
    """
    The role and current state of a player in a game. 

    Each User is a Player in each game that they are in. Each Game has a Player for each player in it. 
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'))
    user_id = Column(UUIDType, ForeignKey('users.id'))

    role = Column(Enum(PlayerRole), nullable=False)
    state = Column(Enum(PlayerState), nullable=False)


class User(Base):
    """
    Details of each user, recognised by their session id

    A user can be in multiple games and will have a GameRole in each
    """
    __tablename__ = "users"

    id = Column(UUIDType,
                primary_key=True,
                nullable=False)
    name = Column(String)
    name_is_generated = Column(Boolean, default=True)

    player_roles = relationship(
        'Player', backref='user', lazy=True)


# many-to-many relationship between players and messages
association_table = Table(
    'message_visibility', Base.metadata,
    Column('player_id', Integer, ForeignKey('players.id')),
    Column('message_id', Integer, ForeignKey('messages.id'))
)


class Message(Base):
    """
    A message in the chatlog of a game. Each Game can have many Messages. 
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String)
    game_id = Column(Integer, ForeignKey('games.id'))
    is_strong = Column(Boolean, default=False)

    visible_to = relationship("Player", secondary=association_table)


def hash_game_id(text: str, N: int = 3):
    """ Hash a string into an N-byte integer

    This method is used to convert the four-word style game identifiers into
    a database-friendly integer. 
    """

    hash_obj = hashlib.md5(text.encode())
    hash_bytes = list(hash_obj.digest())

    # Slice off the first N bytes and cast to integer
    return int.from_bytes(hash_bytes[0:N], 'big')
