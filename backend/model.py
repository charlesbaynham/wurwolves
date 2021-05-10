import datetime
import enum
import json
import logging
import random
from typing import Callable
from typing import Dict
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
    time_created = Column(DateTime, server_default=func.now())

    update_tag = Column(Integer(), default=random_counter_value)

    stage = Column(Enum(GameStage), default=GameStage.LOBBY)
    stage_id = Column(Integer, default=0)

    # Optional settings to customise the role distribution. Must be json
    # parsable to a DistributionSettings object
    distribution_settings = Column(JSONEncodedDict, default=None)

    # Used when a stage has to be repeated, e.g. because a vote tied
    num_attempts_this_stage = Column(Integer, default=0)

    players = relationship("Player", backref="game", lazy=True)

    messages = relationship("Message", backref="game", lazy=True, order_by="Message.id")

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
    FOOL = "Fool"


class PlayerState(str, enum.Enum):
    ALIVE = "ALIVE"
    WOLFED = "WOLFED"
    SHOT = "SHOT"
    LYNCHED = "LYNCHED"
    NOMINATED = "NOMINATED"
    SECONDED = "SECONDED"
    SPECTATING = "SPECTATING"

    def is_dead(self):
        return self in [
            PlayerState.WOLFED,
            PlayerState.SHOT,
            PlayerState.LYNCHED,
            PlayerState.SPECTATING,
        ]


DEAD_STATES = [PlayerState.WOLFED, PlayerState.SHOT, PlayerState.LYNCHED]


class Player(Base):
    """
    The role and current state of a player in a game.

    Each User is a Player in each game that they are in. Each Game has a Player for each player in it.
    """

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, nullable=False)
    time_created = Column(DateTime, server_default=func.now())

    last_seen = Column(DateTime, default=func.now())
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(UUIDType, ForeignKey("users.id"))
    votes = Column(Integer, default=0)
    active = Column(Boolean, default=True)

    role = Column(Enum(PlayerRole), nullable=False)
    state = Column(Enum(PlayerState), nullable=False)

    seed = Column(Float, default=lambda: random.random())

    previous_role = Column(Enum(PlayerRole), nullable=True)

    user = relationship("User", lazy="joined", foreign_keys=user_id)

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
        self.last_seen = datetime.datetime.now()


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, nullable=False)
    time_created = Column(DateTime, server_default=func.now())

    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    stage_id = Column(Integer, index=True, nullable=False)
    selected_player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    stage = Column(Enum(GameStage), nullable=False)
    expired = Column(Boolean, default=False)

    # These fields aren't actually needed or used by the code, since we can
    # determine a player's role by checking the player relationship. However,
    # without these, I can't reproduce games from archived actions.
    role = Column(Enum(PlayerRole), nullable=False)

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
    time_created = Column(DateTime, server_default=func.now())
    name = Column(String)
    name_is_generated = Column(Boolean, default=True)

    player_roles = relationship("Player", lazy=True)


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
    time_created = Column(DateTime, server_default=func.now())

    text = Column(String)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    is_strong = Column(Boolean, default=False)

    visible_to = relationship("Player", secondary=association_table, lazy="joined")

    expired = Column(Boolean, default=False)


def hash_game_tag(text: str):
    """Hash a game id into a 3-byte integer

    A game ID will normally be something like "correct-horse-battery-staple",
    but can actually be any string
    """

    # Replace all spaces with '-' and convert to lower case
    s = text.replace(" ", "-").lower()
    logging.debug("Hashing game tag '%s' to '%s'", text, s)
    return hash_str_to_int(s, 3)


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
    expired: bool

    visible_to: List[PlayerModel]

    class Config:
        orm_mode = True
        extra = "forbid"


class GameModel(pydantic.BaseModel):
    id: int
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


class DistributionSettings(pydantic.BaseModel):
    """Settings for how to generate a game"""

    number_of_wolves: Optional[int] = None
    probability_of_villager: Optional[float] = None
    role_weights: Optional[Dict[PlayerRole, float]] = None

    def is_default(self) -> bool:
        return (
            self.number_of_wolves is None
            and self.role_weights is None
            and self.probability_of_villager is None
        )

    @pydantic.validator("probability_of_villager", always=True)
    def prob(cls, v, values):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("probability_of_villager must be between 0 and 1")
        return v


class FrontendState(pydantic.BaseModel):
    """
    Schema for the React state of a client's frontend
    """

    state_hash: int

    class UIPlayerState(pydantic.BaseModel):
        id: UUID
        name: str
        # Player state. One of PlayerState
        status: str
        # PlayerRole to display. Players will appear as villagers unless they should be revealed
        role: str
        # Random float from 0-1.
        # Will be used by the frontend to decide which picture to display if multiple are available
        seed: float
        # Show this player as having completed their actions this round
        ready: bool = False

        @pydantic.validator("status")
        def status_valid(cls, v):
            try:
                PlayerState(v)
            except ValueError:
                assert v in ["MAYOR"]
            return v

        @pydantic.validator("role")
        def role_valid(cls, v):
            PlayerRole(v)
            return v

    players: List[UIPlayerState]

    class ChatMsg(pydantic.BaseModel):
        msg: str
        isStrong = False

    chat: List[ChatMsg]
    showSecretChat = False

    stage: GameStage

    class RoleState(pydantic.BaseModel):
        title: str
        text: str
        role: str
        button_visible: bool
        button_enabled: bool
        button_text: Union[None, str] = None
        button_confirm_text: Union[None, str] = None
        button_submit_func: Union[None, str] = None
        button_submit_person: Union[None, bool] = None

        seed: float

        @pydantic.validator("role")
        def role_valid(cls, v):
            PlayerRole(v)
            return v

        @pydantic.validator("button_text", always=True)
        def text_present(cls, v, values):
            logging.debug(f"Text = : {v}")
            logging.debug(f"Values = {values}")
            if values["button_visible"] and not v:
                raise ValueError("No button text provided when button is visible")
            return v

    controls_state: RoleState

    myID: UUID
    myName: str
    myNameIsGenerated: bool
    myStatus: PlayerState

    isCustomized: bool


PlayerModel.update_forward_refs()
