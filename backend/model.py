import datetime
import enum
import json
import random
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

import pydantic
import sqlalchemy.sql.functions as func
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import VARCHAR
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
    ENDED = "ENDED"


def random_counter_value():
    return random.randint(1, 2147483646)


class Game(Base):
    """The current state of a game"""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True, nullable=False)
    created = Column(DateTime, default=func.now())

    update_tag = Column(Integer(), default=random_counter_value)

    stage = Column(Enum(GameStage), default=GameStage.LOBBY)
    stage_id = Column(Integer, default=0)

    # Used when a stage has to be repeated, e.g. because a vote tied
    num_attempts_this_stage = Column(Integer, default=0)

    players = relationship("Player", backref="game", lazy=True)

    messages = relationship(
        "Message", backref="game", lazy=True, order_by=lambda: Message.created
    )

    actions = relationship("Action", backref="game", lazy=True)

    def touch(self):
        self.update_tag = random_counter_value()

    def __repr__(self):
        return "<Game id={}, players={}>".format(self.id, self.players)


class PlayerRole(str, enum.Enum):
    VILLAGER = "Villager"
    WOLF = "Wolf"
    SEER = "Seer"
    MEDIC = "Medic"
    JESTER = "Jester"
    SPECTATOR = "Spectator"
    NARRATOR = "Narrator"
    VIGILANTE = "Vigilante"
    MAYOR = "Mayor"
    MILLER = "Miller"
    ACOLYTE = "Acolyte"
    PRIEST = "Priest"
    PROSTITUTE = "Prostitute"
    MASON = "Mason"
    EXORCIST = "Exorcist"


class PlayerState(str, enum.Enum):
    ALIVE = "ALIVE"
    WOLFED = "WOLFED"
    SHOT = "SHOT"
    LYNCHED = "LYNCHED"
    NOMINATED = "NOMINATED"
    SECONDED = "SECONDED"
    SPECTATING = "SPECTATING"


DEAD_STATES = [PlayerState.WOLFED, PlayerState.SHOT, PlayerState.LYNCHED]


class Player(Base):
    """
    The role and current state of a player in a game.

    Each User is a Player in each game that they are in. Each Game has a Player for each player in it.
    """

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, nullable=False)
    last_seen = Column(DateTime, default=func.now())
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(UUIDType, ForeignKey("users.id"))
    votes = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    role = Column(Enum(PlayerRole), nullable=False)
    state = Column(Enum(PlayerState), nullable=False)

    seed = Column(Float, default=lambda: random.random())

    previous_role = Column(Enum(PlayerRole), nullable=True)

    actions = relationship(
        "Action",
        lazy=True,
        foreign_keys="Action.player_id",
        cascade="all, delete-orphan",
    )
    selected_actions = relationship(
        "Action",
        lazy=True,
        foreign_keys="Action.selected_player_id",
        cascade="all, delete-orphan",
    )

    def touch(self):
        self.last_seen = func.now()


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    stage_id = Column(Integer, index=True, nullable=False)
    selected_player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    stage = Column(Enum(GameStage), nullable=False)

    random_field = Column(Integer)

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
    created = Column(DateTime, default=func.now())
    text = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    is_strong = Column(Boolean, default=False)

    visible_to = relationship("Player", secondary=association_table)


def hash_game_tag(text: str):
    """Hash a game id into a 3-byte integer

    A game ID will normally be something like "correct-horse-battery-staple",
    but can actually be any string
    """
    return hash_str_to_int(text, 3)


class PlayerModel(pydantic.BaseModel):
    id: int
    game_id: int
    user_id: UUID
    votes: int = 0
    active: bool = True

    user: "UserModel"

    role: PlayerRole
    state: PlayerState

    seed: float = 0

    previous_role: Optional[PlayerRole]

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
    update_tag: int

    stage: GameStage
    stage_id: int

    num_attempts_this_stage: int

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
    stage: GameStage

    game: GameModel
    player: PlayerModel
    selected_player: Union[None, PlayerModel]

    class Config:
        orm_mode = True
        extra = "forbid"


PlayerModel.update_forward_refs()
