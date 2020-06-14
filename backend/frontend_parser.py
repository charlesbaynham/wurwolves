import json
import logging
import os
from typing import List, Union
from uuid import UUID

import pydantic

from .game import WurwolvesGame
from .model import Game, Player, hash_game_tag
from .database import session_scope


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
        button_text: Union[None, str] = None
        button_confirm_text: Union[None, str] = None
        button_submit_url: Union[None, str] = None
        button_submit_person: Union[None, bool] = None

    role: RoleState

    myID: UUID


def parse_game_to_state(game_tag: str, user_id: UUID):
    '''
    Gets the requested Game and parses it into a FrontendState for viewing by the user user_id
    '''
    g = WurwolvesGame(game_tag)
    game = g.get_game_model()
    player = g.get_player_model(user_id)

    logging.info("Game: %s", game)
    logging.info("Game players: %s", game.players)
    logging.info("Player: %s", player)
    logging.info("User id: %s", user_id)

    state = FrontendState(
        players=[
            FrontendState.PlayerState(
                id=p.user_id,
                name=p.user.name,
                status=p.state,
                selected=False
            ) for p in game.players
        ],
        chat=game.messages,
        stage=game.stage,
        role=FrontendState.RoleState(
            title='Hello',
            day_text='I\'m the daytime',
            night_text='I\'m the nighttime',
            button_visible=False,
            button_enabled=False,
        ),
        myID=user_id
    )

    return state
