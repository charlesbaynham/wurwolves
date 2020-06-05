import enum
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
    GAME = 3


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    See https://docs.sqlalchemy.org/en/13/core/custom_types.html#marshal-json-strings

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
    created = Column(DateTime, onupdate=datetime.utcnow())

    game_id = Column(Integer, index=True)
    event_type = Column(Enum(EventType))
    details = Column(JSONEncodedDict)
    public_visibility = Column(Boolean)

    users_with_visibility = relationship(
        'GameEventVisibility', backref='event', lazy=True)

    def __repr__(self):
        return '<GameEvent {}, type={}>'.format(self.id, self.event_type)


class GameEventVisibility(Base):
    """
    List of users with visibility of a GameEvent

    Only relevant for event_type == GUI and if public_visibility == False
    """
    __tablename__ = "game_event_visibilities"

    id = Column(Integer, primary_key=True, nullable=False)
    event_id = Column(Integer, ForeignKey('game_events.id'))
    user_id = Column(UUIDType)
