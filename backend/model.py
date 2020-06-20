import datetime
import enum
import json
from typing import List, Union
from uuid import UUID

import pydantic
import sqlalchemy.sql.functions as func
from sqlalchemy.sql import text
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, TypeDecorator
from sqlalchemy_utils import UUIDType

from .utils import hash_str_to_int

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


class GameStage(str, enum.Enum):
    LOBBY = "LOBBY"
    DAY = "DAY"
    VOTING = "VOTING"
    NIGHT = "NIGHT"


def update_game_counter(context):
    val = context.get_current_parameters()["update_counter"]
    return val + 1 if val else 1


class Game(Base):
    """The current state of a game"""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    created = Column(DateTime, default=func.now())

    @declared_attr
    def update_counter(cls):
        return Column(Integer(), default=1, onupdate=text("update_counter + 1"))

    stage = Column(Enum(GameStage), default=GameStage.LOBBY)
    stage_id = Column(Integer, default=0)
    start_votes = Column(Integer, default=0)

    players = relationship("Player", backref="game", lazy=True)

    messages = relationship("Message", backref="game", lazy=True)

    actions = relationship("Action", backref="game", lazy=True)

    def touch(self):
        self.update_counter += 1

    def __repr__(self):
        return "<Game id={}, players={}>".format(self.id, self.players)


class PlayerRole(enum.Enum):
    VILLAGER = "VILLAGER"
    WOLF = "WOLF"
    SEER = "SEER"
    MEDIC = "MEDIC"
    JESTER = "JESTER"
    SPECTATOR = "SPECTATOR"


class PlayerState(str, enum.Enum):
    ALIVE = "ALIVE"
    WOLFED = "WOLFED"
    LYNCHED = "LYNCHED"
    NOMINATED = "NOMINATED"
    SECONDED = "SECONDED"
    SPECTATING = "SPECTATING"


class Player(Base):
    """
    The role and current state of a player in a game. 

    Each User is a Player in each game that they are in. Each Game has a Player for each player in it. 
    """

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(UUIDType, ForeignKey("users.id"))

    role = Column(Enum(PlayerRole), nullable=False)
    state = Column(Enum(PlayerState), nullable=False)
    actions = relationship("Action", lazy=True, foreign_keys="Action.player_id")


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    stage_id = Column(Integer, index=True, nullable=False)
    selected_player_id = Column(Integer, ForeignKey("players.id"), nullable=True)

    player = relationship("Player", lazy=True, foreign_keys=player_id)
    selected_player = relationship("Player", lazy=True, foreign_keys=selected_player_id)


class User(Base):
    """
    Details of each user, recognised by their session id

    A user can be in multiple games and will have a GameRole in each
    """

    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True, nullable=False)
    name = Column(String)
    name_is_generated = Column(Boolean, default=True)

    player_roles = relationship("Player", backref="user", lazy=True)


# many-to-many relationship between players and messages
association_table = Table(
    "message_visibility",
    Base.metadata,
    Column("player_id", Integer, ForeignKey("players.id")),
    Column("message_id", Integer, ForeignKey("messages.id")),
)


class Message(Base):
    """
    A message in the chatlog of a game. Each Game can have many Messages. 
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    is_strong = Column(Boolean, default=False)

    visible_to = relationship("Player", secondary=association_table)


def hash_game_tag(text: str):
    """ Hash a game id into a 3-byte integer

    A game ID will normally be something like "correct-horse-battery-staple",
    but can actually be any string
    """
    return hash_str_to_int(text, 3)


class PlayerModel(pydantic.BaseModel):
    id: int
    game_id: int
    user_id: UUID

    user: "UserModel"

    role: PlayerRole
    state: PlayerState

    class Config:
        orm_mode = True
        extra = "forbid"


class MessageModel(pydantic.BaseModel):
    id: int
    text: str
    game_id: int
    is_strong: bool

    visible_to: List[PlayerModel]

    class Config:
        orm_mode = True
        extra = "forbid"


class GameModel(pydantic.BaseModel):
    id: int
    created: datetime.datetime
    update_counter: int

    stage: GameStage
    stage_id: int

    players: List[PlayerModel]
    messages: List[MessageModel]

    class Config:
        orm_mode = True
        extra = "forbid"


class UserModel(pydantic.BaseModel):
    id: UUID
    name: str
    name_is_generated: bool

    class Config:
        orm_mode = True
        extra = "forbid"


class ActionModel(pydantic.BaseModel):
    id: int
    game_id: int
    player_id: int
    stage_id: int
    selected_player_id: Union[int, None]

    game: GameModel
    player: PlayerModel
    selected_player: Union[None, PlayerModel]

    class Config:
        orm_mode = True
        extra = "forbid"


PlayerModel.update_forward_refs()
