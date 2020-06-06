import enum
import hashlib
import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, TypeDecorator
from sqlalchemy_utils import UUIDType

Base = declarative_base()


class EventType(enum.Enum):
    GUI = 1
    CHAT = 2
    NEW_PLAYER = 3


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    See
    https://docs.sqlalchemy.org/en/13/core/custom_types.html#marshal-json-strings

    Usage::
        JSONEncodedDict(255)
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class GameEvent(Base):
    """Event log for all games"""
    __tablename__ = "game_events"

    id = Column(Integer,
                primary_key=True,
                nullable=False)
    created = Column(DateTime, default=datetime.utcnow())

    game_id = Column(Integer, index=True, nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    details = Column(JSONEncodedDict)
    public_visibility = Column(Boolean, default=False)

    users_with_visibility = relationship(
        'GameEventVisibility', backref='event', lazy=True)

    def __repr__(self):
        return '<GameEvent {}, game_id={}, type={}>'.format(self.id, self.game_id, self.event_type)


class GameEventVisibility(Base):
    """
    List of users with visibility of a GameEvent

    Only relevant for event_type == GUI and if public_visibility == False
    """
    __tablename__ = "game_event_visibilities"

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey('game_events.id'))
    user_id = Column(UUIDType)


def hash_game_id(text: str, N: int = 4):
    """ Hash a string into an N-byte integer

    This method is used to convert the four-word style game identifiers into
    a database-friendly integer. 
    """

    hash_obj = hashlib.md5(text.encode())
    hash_bytes = list(hash_obj.digest())

    # Slice off the first N bytes and cast to integer
    return int.from_bytes(hash_bytes[0:N], 'big')
