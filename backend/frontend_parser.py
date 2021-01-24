import logging
import random
import time
from typing import List
from typing import Union
from uuid import UUID

import pydantic

from .model import GameStage
from .model import PlayerRole
from .model import PlayerState


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
