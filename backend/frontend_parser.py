import json
import os
from typing import List, Union
from uuid import UUID
from uuid import uuid4 as uuid

import pydantic


class FrontendState(pydantic.BaseModel):
    '''
    Schema for the React state of a client's frontend
    '''

    class PlayerState(pydantic.BaseModel):
        id: UUID
        name: str
        status: str
        selected: bool = False

    players: List[PlayerState]

    class ChatMsg(pydantic.BaseModel):
        msg: str
        isStrong = False

    chat: List[ChatMsg]

    stage: str

    class RoleState(pydantic.BaseModel):
        title: str
        day_text: str
        night_text: str
        button_visible: bool
        button_enabled: bool
        button_text: Union[None, str]
        button_confirm_text: Union[None, str]
        button_submit_url: Union[None, str]
        button_submit_person: Union[None, bool]

    role: RoleState

    myID: str


class FrontendParser:
    '''
    Parses a Game object into a FrontendState to be given to a user's React frontend
    '''
    pass


SAMPLE_MODEL = os.path.join(os.path.dirname(__file__), 'sample_frontend_state.json')

with open(SAMPLE_MODEL, 'r') as F:
    DEMO_STATE = FrontendState.parse_obj(json.load(F))
